DB_USER = "postgres"
DB_PASSWORD = "ADMIN123"
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "rag_pgvector_db"

DATABASE_URL = (
    f"postgresql+psycopg2://{DB_USER}:{DB_PASSWORD}"
    f"@{DB_HOST}:{DB_PORT}/{DB_NAME}"
)