from typing import List
from openai import OpenAI
from sqlalchemy.orm import Session
from app.config import settings
from app.models import NormativaChunk
from app.schemas import NormativaResult


class NormativaSearchService:
    def __init__(self, db: Session):
        self.db = db
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)

    def _get_query_embedding(self, query: str) -> List[float]:
        """Genera el vector de la consulta en 1536 dimensiones."""
        response = self.client.embeddings.create(
            model=settings.EMBEDDING_MODEL,
            input=query
        )
        return response.data[0].embedding

    def search_similar_chunks(self, query: str, top_k: int = 3) -> List[NormativaResult]:
        """
        Ejecuta la búsqueda semántica utilizando el operador de distancia coseno (<=>) de pgvector.
        Aprovecha el índice HNSW definido en PostgreSQL.
        """
        query_vector = self._get_query_embedding(query)

        # Calculamos la distancia coseno con el operador nativo <=>
        # cosine_distance = NormativaChunk.embedding.cosine_distance(query_vector)
        cosine_distance = NormativaChunk.embedding.cosine_distance(query_vector)
        similarity_expr = (1.0 - cosine_distance).label("similarity_score")

        # Query ejecutada directamente contra el índice HNSW
        query_results = (
            self.db.query(NormativaChunk, similarity_expr)
            .order_by(cosine_distance.asc())
            .limit(top_k)
            .all()
        )

        results: List[NormativaResult] = []
        for chunk, similarity in query_results:
            results.append(
                NormativaResult(
                    id=chunk.id,
                    documento=chunk.documento,
                    titulo=chunk.titulo,
                    capitulo=chunk.capitulo,
                    seccion=chunk.seccion,
                    articulo=chunk.articulo,
                    contenido=chunk.contenido,
                    similarity_score=round(float(similarity), 4)
                )
            )

        return results