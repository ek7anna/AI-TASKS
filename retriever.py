import sys
import pysolr
from langchain_huggingface import HuggingFaceEmbeddings

# Reconfigure stdout for Windows CMD unicode encoding
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

SOLR_URL = "http://localhost:8983/solr/ppt_rag"

def get_solr_client(solr_url=SOLR_URL):
    return pysolr.Solr(solr_url, timeout=10)

def get_embedding_model():
    print("Loading embedding model...")
    model = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
    print("Embedding model loaded!")
    return model

def search(query, solr_url=SOLR_URL):
    solr = get_solr_client(solr_url)
    embedding_model = get_embedding_model()
    
    query_vector = embedding_model.embed_query(query)
    vector = "[" + ",".join(map(str, query_vector)) + "]"
    
    results = solr.search(
        "*:*",
        fq=f"{{!knn f=embedding topK=5}}{vector}"
    )
    print(f"\nFound {len(results)} results from Solr core 'ppt_rag'\n")
    for result in results:
        print("=" * 60)
        print("ID       :", result.get("id"))
        print("Slide    :", result.get("slide"))
        print("Chunk    :", result.get("chunk"))
        content = result.get("content", "")
        if isinstance(content, list):
            content_str = content[0]
        else:
            content_str = str(content)
        print("Content  :", content_str.encode('ascii', errors='replace').decode('ascii'))
    return results

if __name__ == "__main__":
    while True:
        try:
            query = input("\nEnter search text (or 'exit'): ")
            if query.lower() == "exit":
                break
            search(query)
        except Exception as e:
            print(f"Error during retrieval: {e}")
            break
