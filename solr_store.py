import pysolr
from embeddings import get_embedded_chunks

SOLR_URL = "http://localhost:8983/solr/ppt_rag"

def index_to_solr(ppt_path=None, solr_url=SOLR_URL):
    solr = pysolr.Solr(solr_url, always_commit=True, timeout=10)
    embedded_chunks = get_embedded_chunks(ppt_path)
    
    documents = []
    for chunk in embedded_chunks:
        documents.append({
            "id": f"slide_{chunk['slide']}_chunk_{chunk['chunk']}",
            "slide": chunk["slide"],
            "chunk": chunk["chunk"],
            "content": chunk["text"],
            "embedding": chunk["embedding"]
        })

    solr.delete(q="*:*")
    solr.add(documents)
    print(f"\n[SUCCESS] {len(documents)} documents indexed into Solr core 'ppt_rag'!")
    return len(documents)

if __name__ == "__main__":
    try:
        index_to_solr()
    except Exception as e:
        print(f"\nSolr Indexing Notice: {e}")
        print("Note: To run Solr indexing locally, start Apache Solr at 'http://localhost:8983/solr/ppt_rag'.")
