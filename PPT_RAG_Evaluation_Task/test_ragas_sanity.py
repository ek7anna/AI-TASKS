"""
test_ragas_sanity.py - STEP 4: Official RAGAS Sanity Test using Ollama mistral
"""

import sys
import types
import os

# Compatibility shim for ragas on newer langchain_community
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

print("=" * 70)
print("     STEP 4: RAGAS SANITY TEST (ChatOllama mistral format='json')")
print("=" * 70)

# Instantiate ChatOllama with mistral model, format="json", and temperature=0
llm_json = ChatOllama(model="mistral", format="json", temperature=0)
judge_llm = LangchainLLMWrapper(llm_json)

embedding_model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
judge_embeddings = LangchainEmbeddingsWrapper(embedding_model)

# Set judge_llm & judge_embeddings on metrics
faithfulness.llm = judge_llm
context_precision.llm = judge_llm
context_recall.llm = judge_llm
answer_relevancy.llm = judge_llm
answer_relevancy.embeddings = judge_embeddings

dataset = Dataset.from_dict({
    "user_input": ["What is the capital of France?"],
    "response": ["Paris is the capital of France."],
    "retrieved_contexts": [["Paris is the capital of France."]],
    "reference": ["Paris is the capital of France."],
})

run_config = RunConfig(max_workers=1, timeout=120)

print("\nExecuting official ragas.evaluate() on synthetic sample with mistral judge...")
try:
    eval_result = evaluate(
        dataset=dataset,
        metrics=[faithfulness, context_precision, context_recall, answer_relevancy],
        run_config=run_config,
    )
    df = eval_result.to_pandas()
    print("\n" + "=" * 70)
    print("                      SANITY TEST RESULTS")
    print("=" * 70)
    print(df.to_string(index=False))
    
    # Print metric scores
    f_val = df["faithfulness"].iloc[0]
    cp_val = df["context_precision"].iloc[0]
    cr_val = df["context_recall"].iloc[0]
    ar_val = df["answer_relevancy"].iloc[0]

    print("\nSANITY TEST SCORES:")
    print(f"  Faithfulness     : {f_val}")
    print(f"  Context Precision: {cp_val}")
    print(f"  Context Recall   : {cr_val}")
    print(f"  Answer Relevancy : {ar_val}")

    if df.isna().sum().sum() == 0:
        print("\n>>> OVERALL SANITY TEST RESULT: PASS (All 4 metrics produced valid numeric scores)")
    else:
        print("\n>>> OVERALL SANITY TEST RESULT: FAIL (One or more metrics returned NaN)")

except Exception as e:
    print(f"\n[SANITY TEST FAILED] Error:\n{e}")
    import traceback
    traceback.print_exc()
