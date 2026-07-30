import uuid

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from sentence_transformers import SentenceTransformer

from solr_client import add_documents

loader = PyPDFLoader("sample.pdf")
pages = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(pages)

model = SentenceTransformer(
    "sentence-transformers/all-MiniLM-L6-v2"
)

documents = []

for chunk in chunks:

    embedding = model.encode(chunk.page_content)

    documents.append({
        "id": str(uuid.uuid4()),
        "content": chunk.page_content,
        "embedding": embedding.tolist()
    })

add_documents(documents)

print("Documents indexed successfully.")