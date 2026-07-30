from langchain_huggingface import HuggingFaceEmbeddings
from text_splitter import get_slide_chunks

def get_embedded_chunks(ppt_path=None):
    all_chunks = get_slide_chunks(ppt_path)
    print("Loading Hugging Face embedding model (sentence-transformers/all-MiniLM-L6-v2)...")
    embedding_model = HuggingFaceEmbeddings(
        model_name="sentence-transformers/all-MiniLM-L6-v2"
    )
    print("Embedding model loaded successfully!")
    embedded_chunks = []
    for chunk in all_chunks:
        embedding = embedding_model.embed_query(chunk["text"])
        embedded_chunks.append({
            "slide": chunk["slide"],
            "chunk": chunk["chunk"],
            "text": chunk["text"],
            "embedding": embedding
        })
    return embedded_chunks

if __name__ == "__main__":
    try:
        embedded_chunks = get_embedded_chunks()
        print(f"\nGenerated embeddings for {len(embedded_chunks)} chunks\n")
        if embedded_chunks:
            print("Length of one embedding vector:")
            print(len(embedded_chunks[0]["embedding"]))
            print("\nFirst Chunk:")
            print(embedded_chunks[0]["text"].encode('ascii', errors='replace').decode('ascii'))
            print("\nFirst 10 values of its embedding vector:")
            print(embedded_chunks[0]["embedding"][:10])
    except Exception as e:
        print(f"Error generating embeddings: {e}")
