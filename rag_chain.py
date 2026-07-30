import sys
import pysolr
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.chat_message_histories import ChatMessageHistory
from llm import generate_answer, get_llm
from guardrails import run_input_guardrails, run_output_guardrails

# Reconfigure stdout for Windows CMD unicode encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SOLR_URL = "http://localhost:8983/solr/ppt_rag"

# Connect to Solr
solr = pysolr.Solr(SOLR_URL, timeout=10)

# Load embedding model
print("Loading embedding model...")
embedding_model = HuggingFaceEmbeddings(
    model_name="sentence-transformers/all-MiniLM-L6-v2"
)
print("Embedding model loaded!")

# -----------------------------
# Conversational Memory
# -----------------------------
chat_history = ChatMessageHistory()

def retrieve(query):
    # Convert question into embedding
    query_vector = embedding_model.embed_query(query)
    vector = "[" + ",".join(map(str, query_vector)) + "]"
    results = solr.search(
        "*:*",
        fq=f"{{!knn f=embedding topK=5}}{vector}"
    )
    context = ""
    print("\n========== Retrieved Chunks ==========\n")
    for result in results:
        print("=" * 60)
        print("Slide :", result.get("slide", "N/A"))
        print("Chunk :", result.get("chunk", "N/A"))
        content_val = result.get("content", "")
        content_str = content_val[0] if isinstance(content_val, list) else str(content_val)
        print("Content:")
        print(content_str.encode('ascii', errors='replace').decode('ascii'))
        print()
        context += content_str + "\n"
    return context

def ask(question):
    # ---------------------------------------------------------------
    # Build conversation history FIRST
    # ---------------------------------------------------------------
    history = ""
    for message in chat_history.messages:
        if message.type == "human":
            history += f"User: {message.content}\n"
        elif message.type == "ai":
            history += f"Assistant: {message.content}\n"

    # ---------------------------------------------------------------
    # INPUT GUARDRAILS
    #
    # Prompt injection evaluates ONLY raw user question to prevent memory contamination.
    # Off-topic query evaluates expanded context query for follow-up context.
    # ---------------------------------------------------------------
    if history.strip():
        guardrail_query = history + f"\nCurrent question: {question}"
    else:
        guardrail_query = question

    blocked, reason = run_input_guardrails(
        question,
        embedding_model,
        context_question=guardrail_query
    )

    if blocked:
        print(f"\n[GUARDRAIL BLOCKED - INPUT] {reason}")

        answer = (
            "I can't process that request. Please ask a question related to the "
            "HSE Management System / RAG chatbot documentation."
        )

        # Do NOT contaminate chat_history with blocked malicious injection inputs
        return answer

    # ---------------------------------------------------------------
    # RETRIEVAL
    #
    # Use conversation context for follow-up retrieval.
    # ---------------------------------------------------------------
    if history.strip():
        retrieval_query = history + f"\nCurrent question: {question}"
    else:
        retrieval_query = question

    context = retrieve(retrieval_query)

    if context.strip() == "":
        print("\nNo relevant documents found.")

        answer = "I couldn't find the answer in the provided document."

        chat_history.add_user_message(question)
        chat_history.add_ai_message(answer)

        return answer

    print("\n========== Retrieved Context ==========\n")
    print(
        context.encode(
            'ascii',
            errors='replace'
        ).decode('ascii')
    )

    # ---------------------------------------------------------------
    # Generate answer using memory + retrieved context
    # ---------------------------------------------------------------
    answer = generate_answer(
        history=history,
        context=context,
        question=question
    )

    # ---------------------------------------------------------------
    # OUTPUT GUARDRAILS
    # ---------------------------------------------------------------
    flagged, reason = run_output_guardrails(
        answer,
        context,
        embedding_model
    )

    if flagged:
        print(f"\n[GUARDRAIL FLAGGED - OUTPUT] {reason}")

        answer = (
            "I found some information but I'm not confident it directly answers your "
            "question. Please rephrase or ask something more specific to the document."
        )

    print("\n========== AI Answer ==========\n")
    print(answer)

    # ---------------------------------------------------------------
    # Save legitimate turn to conversational memory
    # ---------------------------------------------------------------
    chat_history.add_user_message(question)
    chat_history.add_ai_message(answer)

    return answer

if __name__ == "__main__":
    print("=" * 40)
    print("  PPT Semantic RAG Chatbot")
    print("  Conversational Memory + Guardrails Enabled")
    print("  Type 'exit' to quit")
    print("=" * 40)
    while True:
        question = input("\nAsk: ")
        if question.lower() == "exit":
            print("Goodbye!")
            break
        ask(question)
