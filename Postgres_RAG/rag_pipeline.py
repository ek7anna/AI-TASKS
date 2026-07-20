# ============================================
# IMPORTS
# ============================================

from sqlalchemy import text
from sqlalchemy.orm import Session

from database import engine, SessionLocal
from models import Base, DocumentChunk

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

from sentence_transformers import SentenceTransformer

from transformers import (
    AutoTokenizer,
    AutoModelForCausalLM,
    pipeline,
)

import torch


# ============================================
# DATABASE SETUP
# ============================================

Base.metadata.create_all(engine)

with engine.connect() as conn:
    conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector;"))
    conn.commit()

print("Database Connected Successfully!")


# ============================================
# LOAD PDF
# ============================================

PDF_PATH = "sample.pdf"

loader = PyPDFLoader(PDF_PATH)

documents = loader.load()

print(f"Loaded {len(documents)} pages")


# ============================================
# CHUNK DOCUMENT
# ============================================

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=100,
)

chunks = splitter.split_documents(documents)

print(f"Created {len(chunks)} chunks")


# ============================================
# LOAD EMBEDDING MODEL
# ============================================

embedding_model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

print("Embedding Model Loaded")


# ============================================
# CLEAR OLD DATA
# ============================================

session = SessionLocal()

session.query(DocumentChunk).delete()

session.commit()

print("Old embeddings deleted")


# ============================================
# STORE CHUNKS IN DATABASE
# ============================================

print("Generating embeddings...")

for index, chunk in enumerate(chunks):

    embedding = embedding_model.encode(
        chunk.page_content
    ).tolist()

    record = DocumentChunk(
        filename=PDF_PATH,
        chunk_number=index,
        content=chunk.page_content,
        embedding=embedding,
    )

    session.add(record)

session.commit()

print("All embeddings stored successfully!")
# ============================================
# VECTOR SEARCH FUNCTION
# ============================================

def retrieve_context(question, top_k=3):

    question_embedding = embedding_model.encode(question).tolist()

    sql = text("""
    SELECT
        content,
        embedding <=> CAST(:embedding AS vector) AS distance
    FROM document_chunks
    ORDER BY embedding <=> CAST(:embedding AS vector)
    LIMIT :top_k;
    """)

    result = session.execute(
        sql,
        {
            "embedding": str(question_embedding),
            "top_k": top_k
        }
    )

    context = ""

    print("\nRetrieved Chunks\n")

    for row in result:

        print("-" * 60)
        print(row.content[:250])

        context += row.content + "\n"

    return context


# ============================================
# LOAD QWEN MODEL
# ============================================

print("\nLoading Qwen...\n")

MODEL_NAME = "Qwen/Qwen2.5-0.5B-Instruct"

tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)

model = AutoModelForCausalLM.from_pretrained(
    MODEL_NAME,
    torch_dtype="auto",
    device_map="auto"
)

generator = pipeline(
    "text-generation",
    model=model,
    tokenizer=tokenizer
)

print("Qwen Loaded Successfully!")


# ============================================
# RAG ANSWER FUNCTION
# ============================================

def ask_rag(question):

    context = retrieve_context(question)

    prompt = f"""
You are a helpful AI assistant.

Answer ONLY using the context below.
If the answer is not found, say:
"I couldn't find the answer in the document."

Context:
{context}

Question:
{question}
"""

    messages = [
        {"role": "system", "content": "You answer only from the provided context."},
        {"role": "user", "content": prompt},
    ]

    output = generator(
        messages,
        max_new_tokens=150,
        do_sample=False,
    )

    answer = output[0]["generated_text"][-1]["content"]

    print("\n" + "=" * 80)
    print("ANSWER")
    print("=" * 80)
    print(answer)
# ============================================
# INTERACTIVE RAG CHAT
# ============================================

print("\n" + "=" * 80)
print("PostgreSQL + pgvector RAG System")
print("Type 'exit' to quit")
print("=" * 80)

while True:

    question = input("\nAsk a question: ")

    if question.lower() in ["exit", "quit"]:
        print("\nGoodbye!")
        break

    ask_rag(question)


# ============================================
# CLOSE DATABASE SESSION
# ============================================

session.close()