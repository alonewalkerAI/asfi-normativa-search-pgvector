from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import text  # <-- Importar text
from app.database import get_db
from app.schemas import SearchRequest, SearchResponse
from app.services import NormativaSearchService

app = FastAPI(
    title="ASFI Normativa Search Engine - pgvector",
    description=(
        "Microservicio de búsqueda semántica local sobre regulaciones de la ASFI (Bolivia) "
        "utilizando PostgreSQL con pgvector y OpenAI Embeddings."
    ),
    version="1.0.0"
)


@app.get("/health", tags=["Health"])
def health_check(db: Session = Depends(get_db)):
    """Verifica la conectividad con la base de datos PostgreSQL."""
    try:
        # En SQLAlchemy 2.0 es obligatorio envolver sentencias raw en text()
        db.execute(text("SELECT 1"))
        return {"status": "ok", "database": "connected"}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"Error de conexión con la base de datos: {str(e)}"
        )


@app.post("/search", response_model=SearchResponse, tags=["Search"])
def search_normativa(
    payload: SearchRequest,
    db: Session = Depends(get_db)
):
    """
    Endpoint principal de búsqueda semántica:
    1. Vectoriza la consulta del usuario.
    2. Realiza escaneo indexado HNSW por distancia coseno en PostgreSQL.
    3. Retorna los fragmentos normativos con mayor relevancia semántica.
    """
    try:
        service = NormativaSearchService(db=db)
        results = service.search_similar_chunks(
            query=payload.query,
            top_k=payload.top_k
        )
        return SearchResponse(
            query=payload.query,
            total_results=len(results),
            results=results
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo durante la búsqueda semántica: {str(e)}"
        )