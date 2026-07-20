# solr_client.py

import pysolr
from config import SOLR_URL

# Connect to Solr
solr = pysolr.Solr(SOLR_URL, always_commit=True)


def add_documents(documents):
    """
    Upload document chunks and embeddings to Solr.
    """
    solr.add(documents)
    print(f"Indexed {len(documents)} document chunks.")


def search(query_embedding, top_k=3):
    """
    Perform vector similarity search using Solr KNN.
    """
    embedding_str = ",".join(map(str, query_embedding))

    results = solr.search(
        "*:*",
        **{
            "rows": top_k,
            "fl": "id,content,score",
            "fq": "{!knn f=embedding topK=%d}[%s]" % (top_k, embedding_str)
        }
    )

    return results