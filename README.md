# ASFI Normativa Search con pgvector

Microservicio de búsqueda semántica sobre normativa de la Autoridad de Supervisión del Sistema Financiero (ASFI) de Bolivia. Combina FastAPI, PostgreSQL con la extensión `pgvector` y embeddings de OpenAI para recuperar fragmentos normativos relevantes a partir de preguntas en lenguaje natural.

> **Estado:** proyecto demostrativo. El script de ingesta incluye cinco fragmentos de ejemplo; no contiene una copia integral ni oficial de la normativa ASFI.

## Características

- API REST con FastAPI.
- Búsqueda semántica mediante similitud coseno.
- Índice HNSW de pgvector para consultas vectoriales eficientes.
- PostgreSQL 16 con pgvector, listo para ejecutar con Docker Compose.
- Validación de solicitudes y respuestas con Pydantic.

## Arquitectura

1. `ingest.py` genera embeddings para los fragmentos normativos y los guarda en PostgreSQL.
2. `POST /search` vectoriza la consulta del usuario con OpenAI.
3. PostgreSQL ordena los fragmentos con distancia coseno usando el índice HNSW.
4. La API devuelve los resultados junto con su puntuación de similitud.

## Requisitos

- Python 3.11 o superior.
- Docker y Docker Compose.
- Una clave de API de OpenAI con acceso al modelo de embeddings configurado.

## Instalación

1. Clone el repositorio y entre en la carpeta del proyecto.

   ```powershell
   git clone https://github.com/USUARIO/asfi-normativa-search-pgvector.git
   cd asfi-normativa-search-pgvector
   ```

2. Cree y active un entorno virtual.

   ```powershell
   python -m venv venv
   .\venv\Scripts\Activate.ps1
   ```

3. Instale las dependencias.

   ```powershell
   pip install -r requirements.txt
   ```

4. Cree su configuración local a partir de la plantilla.

   ```powershell
   Copy-Item .env.example .env
   ```

5. Edite `.env` e indique, como mínimo, una `OPENAI_API_KEY` válida. No suba este archivo al repositorio.

6. Inicie PostgreSQL con pgvector.

   ```powershell
   docker compose up -d
   ```

7. Cargue los datos de demostración. **Este comando borra los registros existentes de `normativa_chunks` antes de insertar el dataset de ejemplo.**

   ```powershell
   python ingest.py
   ```

8. Ejecute la API.

   ```powershell
   uvicorn app.main:app --reload
   ```

La documentación interactiva estará disponible en `http://localhost:8000/docs`.

## Configuración

| Variable | Descripción | Valor de ejemplo |
| --- | --- | --- |
| `DB_USER` | Usuario de PostgreSQL | `asfi_admin` |
| `DB_PASSWORD` | Contraseña de PostgreSQL | `cambie_esta_contrasena` |
| `DB_NAME` | Nombre de la base de datos | `asfi_normativa` |
| `DB_HOST` | Host de PostgreSQL | `localhost` |
| `DB_PORT` | Puerto de PostgreSQL | `5432` |
| `OPENAI_API_KEY` | Clave de API de OpenAI | `sk-...` |
| `EMBEDDING_MODEL` | Modelo de embeddings | `text-embedding-3-small` |
| `EMBEDDING_DIMENSION` | Dimensión de los vectores | `1536` |

La dimensión del modelo debe coincidir con la definida en `sql/init.sql` y en la variable `EMBEDDING_DIMENSION`.

## Uso de la API

### Comprobar el estado

```powershell
Invoke-RestMethod http://localhost:8000/health
```

Respuesta esperada:

```json
{"status":"ok","database":"connected"}
```

### Buscar normativa

```powershell
$body = @{ query = "autenticación de dos pasos para pagos móviles"; top_k = 3 } | ConvertTo-Json
Invoke-RestMethod -Uri http://localhost:8000/search -Method Post -ContentType "application/json" -Body $body
```

También puede ejecutar los casos incluidos:

```powershell
python app/test_search.py
```

## Estructura

```text
app/
  config.py       # Carga de configuración desde .env
  database.py     # Conexión y sesiones SQLAlchemy
  main.py         # Endpoints FastAPI
  models.py       # Modelo ORM y vector pgvector
  schemas.py      # Esquemas Pydantic
  services.py     # Embeddings y búsqueda semántica
  test_search.py  # Pruebas manuales contra la API
sql/init.sql      # Extensión, tabla e índice HNSW
docker-compose.yml
ingest.py         # Ingesta del dataset de demostración
```

## Seguridad y operación

- `.env`, entornos virtuales y datos persistentes locales están excluidos por `.gitignore`.
- Defina `DB_PASSWORD` en `.env`; no use la contraseña predeterminada del archivo Compose en entornos compartidos o de producción.
- Las consultas a `/search` consumen la API de embeddings de OpenAI y pueden generar costos.
- La API no incorpora autenticación, autorización, límites de tasa ni manejo específico de errores de proveedores. Añada estas medidas antes de exponerla públicamente.

## Licencia

No se ha definido una licencia para este proyecto. Agregue una antes de distribuir o reutilizar el código públicamente.
