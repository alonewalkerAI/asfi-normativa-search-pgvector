from sqlalchemy import Column, Integer, String, Text, DateTime, func
from pgvector.sqlalchemy import Vector
from app.database import Base
from app.config import settings


class NormativaChunk(Base):
    __tablename__ = "normativa_chunks"

    id = Column(Integer, primary_key=True, index=True)
    documento = Column(String(255), nullable=False)
    titulo = Column(String(255), nullable=False)
    capitulo = Column(String(255), nullable=False)
    seccion = Column(String(255), nullable=True)
    articulo = Column(String(100), nullable=False)
    contenido = Column(Text, nullable=False)
    embedding = Column(Vector(settings.EMBEDDING_DIMENSION), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())