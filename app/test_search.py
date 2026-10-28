import json
import urllib.request

URL = "http://localhost:8000/search"

CASOS_DE_PRUEBA = [
    {
        "caso": "Banca Digital y Fraude",
        "query": "autenticación de dos pasos y token para pagos móviles",
        "top_k": 1,
    },
    {
        "caso": "Gestión de Desastres y Continuidad",
        "query": "cada cuánto tiempo se debe probar el plan de contingencia ante caídas del sistema",
        "top_k": 1,
    },
    {
        "caso": "Capacidad de Pago de Clientes",
        "query": "qué debe analizar el banco para prestar dinero además de las garantías",
        "top_k": 1,
    },
]

print("=== INICIANDO PRUEBAS SEMÁNTICAS CONTRA LA API ===")

for item in CASOS_DE_PRUEBA:
    payload = json.dumps({"query": item["query"], "top_k": item["top_k"]}).encode(
        "utf-8"
    )
    req = urllib.request.Request(
        URL, data=payload, headers={"Content-Type": "application/json"}
    )

    try:
        with urllib.request.urlopen(req) as response:
            res_data = json.loads(response.read().decode("utf-8"))
            print(f"\n[Test: {item['caso']}]")
            print(f"Pregunta: '{item['query']}'")
            if res_data["results"]:
                top = res_data["results"][0]
                print(f"-> Artículo recuperado: {top['articulo']}")
                print(f"-> Título: {top['titulo']}")
                print(f"-> Score Similitud: {top['similarity_score']}")
            else:
                print("-> Sin resultados.")
    except Exception as e:
        print(f"Error en consulta '{item['caso']}': {e}")

print("\n=== PRUEBAS FINALIZADAS ===")