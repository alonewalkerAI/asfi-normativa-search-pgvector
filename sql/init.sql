-- Habilitar la extensión de pgvector en PostgreSQL
CREATE EXTENSION IF NOT EXISTS vector;

-- Tabla para almacenar fragmentos normativos y sus representaciones vectoriales
CREATE TABLE IF NOT EXISTS normativa_chunks (
    id SERIAL PRIMARY KEY,
    documento VARCHAR(255) NOT NULL,       -- Ej: "Recopilación de Normas para Servicios Financieros"
    titulo VARCHAR(255) NOT NULL,          -- Ej: "Título II - Gestión de Riesgos"
    capitulo VARCHAR(255) NOT NULL,        -- Ej: "Capítulo I - Riesgo Operativo"
    seccion VARCHAR(255),                  -- Ej: "Sección 3 - Medidas Preventivas"
    articulo VARCHAR(100) NOT NULL,        -- Ej: "Artículo 4"
    contenido TEXT NOT NULL,               -- Texto normativo completo del fragmento
    embedding vector(1536) NOT NULL,       -- Vector generado por OpenAI text-embedding-3-small
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índice HNSW optimizado para distancia Coseno (vector_cosine_ops)
-- m=16: número de conexiones bidireccionales por nodo
-- ef_construction=64: tamaño de la lista dinámica durante la indexación
CREATE INDEX IF NOT EXISTS idx_normativa_chunks_embedding_hnsw
ON normativa_chunks
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);
