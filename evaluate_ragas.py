"""
evaluate_ragas.py - OFFICIAL RAGAS Library Evaluation with Ollama mistral Judge & LangSmith Telemetry

Architecture:
  - Chatbot Generator: Ollama llama3.2 (100% preserved)
  - Vector Store    : Apache Solr core 'ppt_rag' (100% preserved)
  - RAGAS Judge     : Ollama mistral (format="json")
  - Embeddings      : sentence-transformers/all-MiniLM-L6-v2

Features:
  1. Uses ChatOllama(model="mistral", format="json", temperature=0) as the RAGAS judge.
  2. Preserves exact Solr retrieved chunk boundaries as retrieved_contexts = [chunk1, chunk2, ...].
  3. No fillna(0.0) — NaNs/failures remain explicit as FAILED/NaN.
  4. Logs valid official RAGAS metric scores to LangSmith traces as feedback.
  5. Exports ragas_results_table.csv, ragas_evaluation_results.json, and dynamic failure_analysis.md.
"""

import sys
import types
import os
import json
import pysolr
import pandas as pd

# Compatibility shim for ragas on newer langchain_community releases
if 'langchain_community.chat_models.vertexai' not in sys.modules:
    dummy_vertex = types.ModuleType('langchain_community.chat_models.vertexai')
    dummy_vertex.ChatVertexAI = None
    sys.modules['langchain_community.chat_models.vertexai'] = dummy_vertex

# Reconfigure stdout for Windows CMD encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from datasets import Dataset
from ragas import evaluate
from ragas.run_config import RunConfig
from ragas.metrics import (
    faithfulness,
    context_precision,
    context_recall,
    answer_relevancy,
)
from ragas.llms import LangchainLLMWrapper
from ragas.embeddings import LangchainEmbeddingsWrapper
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_ollama import ChatOllama

# LangSmith configuration
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_ENDPOINT"] = "https://api.smith.langchain.com"
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", "PPT-Semantic-RAG-Evaluation")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY", "")

from langsmith import Client
from langchain_core.tracers.context import collect_runs

# Import real pipeline components
from rag_chain import generate_answer
from llm import get_llm

SOLR_URL = "http://localhost:8983/solr/ppt_rag"
solr = pysolr.Solr(SOLR_URL, timeout=10)

TEST_QUESTIONS = [
    {
        "question": "What is ChromaDB and how is it used in the project?",
        "ground_truth": (
            "ChromaDB is a vector database used to build an in-memory vector store "
            "that allows users to upload a PDF interactively and perform similarity search "
            "without requiring an external database server."
        ),
    },
    {
        "question": "What embedding model is used for generating dense vectors in this pipeline?",
        "ground_truth": (
            "The pipeline uses sentence-transformers/all-MiniLM-L6-v2 via LangChain's "
            "HuggingFaceEmbeddings to generate 384-dimensional dense vectors."
        ),
    },
    {
        "question": "How is Apache Solr queried for vector search in rag_chain.py?",
        "ground_truth": (
            "Apache Solr is queried using a k-nearest-neighbor filter "
            "{!knn f=embedding topK=5} passed via the fq parameter in pysolr "
            "to retrieve the top 5 closest chunk vectors."
        ),
    },
    {
        "question": "What happens if a user types a generic greeting like 'hey'?",
        "ground_truth": (
            "When a generic greeting like 'hey' is typed, Solr KNN still returns "
            "top-K nearest chunks, but since none contain an answer to 'hey', the "
            "LLM prompt instructs it to fall back to "
            "'I couldn't find the answer in the provided document.'"
        ),
    },
    {
        "question": "Give some examples of incident management features in the HSE Management System.",
        "ground_truth": (
            "Examples of incident management features include creating, editing, "
            "viewing, deleting, changing status, and assigning tasks to specific "
            "individuals, as well as an incident trend chart and dashboard usage metrics."
        ),
    },
]

def retrieve_chunks(query, embedding_model):
    """Retrieves top 5 chunks from Solr preserving exact chunk boundaries."""
    query_vector = embedding_model.embed_query(query)
    vector_str = "[" + ",".join(map(str, query_vector)) + "]"
    results = solr.search("*:*", fq=f"{{!knn f=embedding topK=5}}{vector_str}")
    
    chunks = []
    for doc in results:
        c = doc.get("content", "")
        if isinstance(c, list):
            c = c[0]
        if c and c.strip():
            chunks.append(c.strip())
    return chunks if chunks else ["(no context retrieved)"]

def run_pipeline_and_capture_traces(questions, embedding_model):
    """Executes each question live through Solr retrieval & Ollama llama3.2 answer generation."""
    llm = get_llm()  # llama3.2
    records = []

    for item in questions:
        q = item["question"]
        chunks = retrieve_chunks(q, embedding_model)
        context_str = "\n".join(chunks)

        with collect_runs() as cb:
            ans = generate_answer(history="", context=context_str, question=q, llm=llm)
            run_id = cb.traced_runs[-1].id if cb.traced_runs else None

        records.append({
            "question": q,
            "ground_truth": item["ground_truth"],
            "retrieved_chunks": chunks,
            "context_str": context_str,
            "answer": ans,
            "run_id": run_id,
        })
        print(f"[OK] Pipeline execution (llama3.2): {q!r} -> run_id={run_id}")

    return records

def score_with_official_ragas(records, embedding_model):
    """Executes official RAGAS evaluation using ChatOllama(model='mistral', format='json')."""
    judge_llm_base = ChatOllama(model="mistral", format="json", temperature=0)
    judge_llm = LangchainLLMWrapper(judge_llm_base)
    judge_embeddings = LangchainEmbeddingsWrapper(embedding_model)

    # Set judge LLM & Embeddings on metric instances
    faithfulness.llm = judge_llm
    context_precision.llm = judge_llm
    context_recall.llm = judge_llm
    answer_relevancy.llm = judge_llm
    answer_relevancy.embeddings = judge_embeddings

    dataset = Dataset.from_dict({
        "user_input": [r["question"] for r in records],
        "response": [r["answer"] for r in records],
        "retrieved_contexts": [r["retrieved_chunks"] for r in records],
        "reference": [r["ground_truth"] for r in records],
    })

    run_config = RunConfig(max_workers=1, timeout=400)

    print("\n[RAGAS] Executing official ragas.evaluate() with mistral JSON judge...")
    eval_result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, context_precision, context_recall, answer_relevancy],
        run_config=run_config,
    )
    
    # Return raw dataframe WITHOUT fillna(0.0) to preserve true metric values / NaNs
    return eval_result.to_pandas()

def log_feedback_to_langsmith(records, scores_df):
    """Logs valid metric scores to LangSmith trace runs (skipping NaNs)."""
    try:
        client = Client()
    except Exception as e:
        print(f"[WARN] Could not initialize LangSmith Client: {e}")
        return

    metric_cols = ["faithfulness", "context_precision", "context_recall", "answer_relevancy"]

    for i, row in scores_df.iterrows():
        run_id = records[i]["run_id"]
        if run_id is None:
            continue
        for metric in metric_cols:
            val = row.get(metric)
            if pd.isna(val):
                print(f"[WARN] Metric {metric} returned NaN for question {i+1}, skipping LangSmith log.")
                continue
            try:
                client.create_feedback(
                    run_id=run_id,
                    key=metric,
                    score=float(val),
                    comment=f"Official RAGAS {metric} for: {records[i]['question']!r}",
                )
            except Exception as e:
                print(f"[WARN] Could not log feedback for run {run_id}: {e}")
        print(f"[OK] Logged official RAGAS feedback to LangSmith run {run_id}")

def main():
    print("=" * 70)
    print("           OFFICIAL RAGAS EVALUATION PIPELINE")
    print("=" * 70)
    print("Metrics  : Faithfulness, Context Precision, Context Recall, Answer Relevancy")
    print("Chatbot  : Ollama llama3.2 (Generation Model)")
    print("RAGAS    : Ollama mistral (format='json' Judge Model)")
    print("Embeddings: sentence-transformers/all-MiniLM-L6-v2")
    print("-" * 70)

    embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")

    print("\n[1/4] Executing live RAG pipeline (Solr retrieve + llama3.2 generate) for 5 questions...")
    records = run_pipeline_and_capture_traces(TEST_QUESTIONS, embedding_model)

    # Print input data for each question for transparency
    print("\n" + "=" * 70)
    print("                  EVALUATION INPUT TRANSPARENCY")
    print("=" * 70)
    for idx, r in enumerate(records):
        print(f"\n--- QUESTION #{idx+1}: {r['question']!r} ---")
        print("RETRIEVED CHUNKS:")
        for ci, ch in enumerate(r['retrieved_chunks']):
            print(f"  [Chunk {ci+1}]: {ch[:150]}...")
        print(f"GENERATED ANSWER : {r['answer']!r}")
        print(f"REFERENCE ANSWER : {r['ground_truth']!r}")

    print("\n[2/4] Scoring dataset with OFFICIAL RAGAS library (mistral judge)...")
    try:
        scores_df = score_with_official_ragas(records, embedding_model)
    except Exception as e:
        print(f"\n[RAGAS ERROR] Official RAGAS evaluation failed with error:\n{e}")
        sys.exit(1)

    print("\n[3/4] Logging official RAGAS feedback scores to LangSmith traces...")
    log_feedback_to_langsmith(records, scores_df)

    print("\n[4/4] Constructing results table & summary benchmarks...")
    rows = []
    for i, r in enumerate(records):
        row = scores_df.iloc[i]
        numeric_scores = [v for v in [row.get("faithfulness"), row.get("context_precision"), row.get("context_recall"), row.get("answer_relevancy")] if not pd.isna(v)]
        mean_score = round(sum(numeric_scores) / len(numeric_scores), 3) if numeric_scores else 0.0

        rows.append({
            "Q#": i + 1,
            "Question": r["question"],
            "Retrieved Context": " | ".join(r["retrieved_chunks"])[:300],
            "Generated Answer": r["answer"],
            "Reference Answer": r["ground_truth"],
            "Faithfulness": "FAILED/NaN" if pd.isna(row.get("faithfulness")) else round(row.get("faithfulness"), 3),
            "Context Precision": "FAILED/NaN" if pd.isna(row.get("context_precision")) else round(row.get("context_precision"), 3),
            "Context Recall": "FAILED/NaN" if pd.isna(row.get("context_recall")) else round(row.get("context_recall"), 3),
            "Answer Relevancy": "FAILED/NaN" if pd.isna(row.get("answer_relevancy")) else round(row.get("answer_relevancy"), 3),
            "Mean RAGAS Score": mean_score,
        })

    df = pd.DataFrame(rows)
    print("\n" + df.to_string(index=False))

    # Calculate overall means ignoring NaNs
    summary = {}
    for col in ["faithfulness", "context_precision", "context_recall", "answer_relevancy"]:
        vals = scores_df[col].dropna()
        summary[col] = round(vals.mean(), 3) if len(vals) > 0 else 0.0

    overall_mean = round(sum(summary.values()) / 4, 3)
    summary["Overall RAGAS Score"] = overall_mean

    print("\n" + "=" * 70)
    print("               SUMMARY OFFICIAL RAGAS BENCHMARK SCORES")
    print("=" * 70)
    for k, v in summary.items():
        print(f"  {k:<30}: {v:.3f}")
    print("=" * 70)

    # Save output deliverables
    df.to_csv("ragas_results_table.csv", index=False, encoding="utf-8")
    with open("ragas_evaluation_results.json", "w", encoding="utf-8") as f:
        json.dump({"results": rows, "summary": summary}, f, indent=2)
    print("\n[SUCCESS] Saved ragas_results_table.csv and ragas_evaluation_results.json")

    # Generate dynamic failure analysis for lowest scorer
    worst_row = df.loc[df["Mean RAGAS Score"].idxmin()]
    with open("failure_analysis.md", "w", encoding="utf-8") as f:
        f.write(f"""# Failure Case Analysis

## Lowest-Scoring Question: "{worst_row['Question']}"

- **Mean RAGAS Score**: {worst_row['Mean RAGAS Score']}
- **Faithfulness**: {worst_row['Faithfulness']}
- **Context Precision**: {worst_row['Context Precision']}
- **Context Recall**: {worst_row['Context Recall']}
- **Answer Relevancy**: {worst_row['Answer Relevancy']}

---

## 🔍 Root Cause Analysis

Based on official RAGAS metric evaluation judged by local Ollama mistral:
- **Question**: `{worst_row['Question']}`
- **Retrieved Context Snippet**: `{worst_row['Retrieved Context']}`
- **Generated Answer**: `{worst_row['Generated Answer']}`
- **Reference Answer**: `{worst_row['Reference Answer']}`

### Detailed Performance Breakdown:
- **Faithfulness ({worst_row['Faithfulness']})**: Evaluates whether claims in the generated answer are explicitly supported by retrieved context.
- **Context Precision ({worst_row['Context Precision']})**: Evaluates whether retrieved Solr chunks contain signal vs noise.
- **Context Recall ({worst_row['Context Recall']})**: Evaluates whether retrieved contexts cover key facts in the reference answer.
- **Answer Relevancy ({worst_row['Answer Relevancy']})**: Evaluates semantic directness of generated answer to the question.

---

## 🛠️ Production Remediation Plan

1. **Query Enhancement**: Implement conversational keyword expansion prior to Solr KNN vector search.
2. **Cross-Encoder Reranking**: Apply `ms-marco-MiniLM-L-6-v2` post-retrieval to re-rank chunks before LLM prompt construction.
""")
    print("[SUCCESS] Saved failure_analysis.md")

if __name__ == "__main__":
    main()