import ollama

from sentence_transformers import SentenceTransformer

from solr_client import search

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

question = input("Ask a question: ")

query_embedding = model.encode(question)

results = search(query_embedding)

context = ""

for doc in results:

    context += doc["content"] + "\n\n"

prompt = f"""
Answer only using the context.

Context:
{context}

Question:
{question}

Answer:
"""

response = ollama.chat(
    model="qwen2.5:0.5b",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
    ]
)

print(response["message"]["content"])