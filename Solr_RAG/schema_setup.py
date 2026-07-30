import requests

SOLR_URL = "http://localhost:8983/solr/rag_core"

payload = {
    "add-field": {
        "name": "embedding",
        "type": "knn_vector",
        "stored": True,
        "indexed": True,
        "dimension": 384,
        "similarityFunction": "cosine"
    }
}

response = requests.post(
    f"{SOLR_URL}/schema",
    json=payload,
    headers={"Content-Type": "application/json"}
)

print(response.status_code)
print(response.text)