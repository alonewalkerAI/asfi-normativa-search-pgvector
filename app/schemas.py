from typing import List, Optional
from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=3,
        max_length=500,
        description="Consulta en lenguaje natural sobre la normativa ASFI",
        examples=["¿Cuál es el capital mínimo requerido para operar?"]
    )
    top_k: int = Field(
        default=3,
        ge=1,
        le=10,
        description="Número máximo de fragmentos normativos a retornar"
    )


class NormativaResult(BaseModel):
    id: int
    documento: str
    titulo: str
    capitulo: str
    seccion: Optional[str]
    articulo: str
    contenido: str
    similarity_score: float = Field(
        ...,
        description="Similitud coseno normalizada (1 - distancia_coseno), entre 0.0 y 1.0"
    )

    class Config:
        from_attributes = True


class SearchResponse(BaseModel):
    query: str
    total_results: int
    results: List[NormativaResult]