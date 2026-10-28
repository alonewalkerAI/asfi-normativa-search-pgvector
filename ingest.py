import sys
from typing import List, Dict
from openai import OpenAI
from app.config import settings
from app.database import SessionLocal
from app.models import NormativaChunk

# Dataset normativo representativo de la RNSF - ASFI
NORMATIVA_DATASET: List[Dict[str, str]] = [
    {
        "documento": "Recopilación de Normas para Servicios Financieros (RNSF)",
        "titulo": "Título II: Gestión de Riesgos",
        "capitulo": "Capítulo I: Gestión del Riesgo Crediticio",
        "seccion": "Sección 2: Evaluación de Capacidad de Pago",
        "articulo": "Artículo 3° (Criterio Fundamental)",
        "contenido": (
            "La evaluación de la capacidad de pago del prestatario es el criterio fundamental "
            "para el otorgamiento de créditos. Las entidades supervisadas deben analizar el flujo "
            "de caja proyectado, los ingresos operativos verificables y el nivel de endeudamiento "
            "global en el sistema financiero, sin depender exclusivamente de las garantías ofrecidas."
        )
    },
    {
        "documento": "Recopilación de Normas para Servicios Financieros (RNSF)",
        "titulo": "Título II: Gestión de Riesgos",
        "capitulo": "Capítulo IV: Gestión del Riesgo Operativo",
        "seccion": "Sección 4: Registro de Eventos de Pérdida",
        "articulo": "Artículo 8° (Base de Datos de Incidentes)",
        "contenido": (
            "Las entidades supervisadas deben implementar y mantener una base de datos histórica "
            "de eventos de pérdida por riesgo operativo. Dicho registro debe contemplar fallas en procesos "
            "internos, errores humanos, interrupciones de los sistemas informáticos, fraude interno, "
            "fraude externo y eventos de fuerza mayor que impacten el patrimonio de la entidad."
        )
    },
    {
        "documento": "Recopilación de Normas para Servicios Financieros (RNSF)",
        "titulo": "Título II: Gestión de Riesgos",
        "capitulo": "Capítulo IX: Gestión de la Continuidad del Negocio",
        "seccion": "Sección 3: Pruebas del Plan de Contingencia",
        "articulo": "Artículo 5° (Frecuencia y Simulación de Desastres)",
        "contenido": (
            "El Plan de Continuidad del Negocio (PCN) y el Plan de Recuperación ante Desastres (DRP) "
            "deben ser evaluados y probados mediante simulaciones operativas al menos una vez al año. "
            "Los resultados de dichas pruebas, incluyendo los tiempos reales de recuperación (RTO y RPO), "
            "deben ser formalmente documentados y remitidos al Comité de Riesgos y al Directorio."
        )
    },
    {
        "documento": "Recopilación de Normas para Servicios Financieros (RNSF)",
        "titulo": "Título V: Seguridad y Tecnología de la Información",
        "capitulo": "Capítulo I: Gestión de Seguridad de la Información",
        "seccion": "Sección 5: Canales Electrónicos y Autenticación",
        "articulo": "Artículo 12° (Mecanismos de Doble Factor)",
        "contenido": (
            "Para la realización de transferencias electrónicas de fondos y pagos por canales digitales, "
            "las entidades de intermediación financiera deben implementar obligatoriamente mecanismos de "
            "autenticación robusta o de doble factor (2FA). Los códigos de uso único (OTP) o tokens "
            "criptográficos deben poseer tiempos de expiración reducidos y controles antifraude."
        )
    },
    {
        "documento": "Recopilación de Normas para Servicios Financieros (RNSF)",
        "titulo": "Título I: Constitución y Licencias",
        "capitulo": "Capítulo III: Requerimientos de Capital",
        "seccion": "Sección 1: Coeficiente de Adecuación Patrimonial",
        "articulo": "Artículo 4° (Límite Mínimo Regulatorio)",
        "contenido": (
            "Las entidades de intermediación financiera deben mantener en todo momento un Coeficiente de "
            "Adecuación Patrimonial (CAP) no menor al diez por ciento (10%) respecto de sus activos y "
            "contingentes ponderados por factores de riesgo crediticio, de mercado y operativo. El incumplimiento "
            "de este ratio activa de forma inmediata planes de regularización obligatorios."
        )
    }
]


def generate_embeddings_batch(texts: List[str]) -> List[List[float]]:
    """Genera embeddings en una sola llamada usando OpenAI."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    response = client.embeddings.create(
        model=settings.EMBEDDING_MODEL,
        input=texts
    )
    return [item.embedding for item in response.data]


def run_ingestion():
    print("=== INICIANDO PIPELINE DE INGESTA NORMATIVA ASFI ===")

    # 1. Preparar textos para embedding
    # Concatenamos título, artículo y contenido para máxima densidad semántica
    texts_to_embed = [
        f"{doc['titulo']} - {doc['articulo']}: {doc['contenido']}"
        for doc in NORMATIVA_DATASET
    ]

    print(f"Generando embeddings para {len(texts_to_embed)} fragmentos normativos...")
    try:
        embeddings = generate_embeddings_batch(texts_to_embed)
        print("Embeddings generados exitosamente con OpenAI.")
    except Exception as e:
        print(f"Error al contactar la API de OpenAI: {e}", file=sys.stderr)
        sys.exit(1)

    # 2. Persistir en PostgreSQL
    db = SessionLocal()
    try:
        print("Verificando registros existentes en 'normativa_chunks'...")
        # Limpieza previa para evitar duplicar si se ejecuta múltiples veces el test
        db.query(NormativaChunk).delete()
        db.commit()

        print("Insertando fragmentos normativos indexados...")
        chunks_to_insert = []
        for doc, emb in zip(NORMATIVA_DATASET, embeddings):
            chunk = NormativaChunk(
                documento=doc["documento"],
                titulo=doc["titulo"],
                capitulo=doc["capitulo"],
                seccion=doc["seccion"],
                articulo=doc["articulo"],
                contenido=doc["contenido"],
                embedding=emb
            )
            chunks_to_insert.append(chunk)

        db.add_all(chunks_to_insert)
        db.commit()
        print(f"Éxito: {len(chunks_to_insert)} registros guardados en PostgreSQL.")

    except Exception as e:
        db.rollback()
        print(f"Error al persistir en la base de datos: {e}", file=sys.stderr)
        sys.exit(1)
    finally:
        db.close()

    print("=== PIPELINE COMPLETADO EXITOSAMENTE ===")


if __name__ == "__main__":
    run_ingestion()
