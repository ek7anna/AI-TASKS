from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text
from pgvector.sqlalchemy import Vector

Base = declarative_base()

class DocumentChunk(Base):

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True)

    filename = Column(String)

    chunk_number = Column(Integer)

    content = Column(Text)

    embedding = Column(Vector(384))