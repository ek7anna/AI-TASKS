# config.py

SOLR_URL = "http://localhost:8983/solr/rag_core"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

LLM_MODEL = "Qwen/Qwen2.5-0.5B-Instruct"

PDF_PATH = "sample.pdf"

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50