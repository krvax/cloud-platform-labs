"""
NIVEL 4: Resumen (Cheat Sheet)

¿Cuándo usar qué? (Pregunta TÍPICA de entrevista SRE/DevOps).

1. TAREA: Llamar a la API de Datadog 500 veces para obtener métricas.
   -> ¿Es I/O o CPU? I/O Bound.
   -> ¿Cuántas peticiones? MUCHAS (500).
   -> DECISIÓN: **AsyncIO**. (Crea poco overhead de memoria).

2. TAREA: Llamar a la base de datos MySQL 10 veces para cruzar datos.
   -> ¿Es I/O o CPU? I/O Bound.
   -> ¿La librería de DB soporta AsyncIO? Si no lo soporta (ej. psycopg2 viejo), 
   -> DECISIÓN: **Threading (ThreadPoolExecutor)**.

3. TAREA: Parsear un JSON Dump de 10GB, encriptarlo con AES-256 y guardarlo.
   -> ¿Es I/O o CPU? CPU Bound (Encriptación masiva).
   -> DECISIÓN: **Multiprocessing (ProcessPoolExecutor)**.
   
4. TAREA: Escribir un pequeño script de Cron para borrar un bucket de S3 con 5 archivos.
   -> DECISIÓN: **Secuencial**. (Mantén la simplicidad, KISS principle).

---

SRE Rule of Thumb:
- Evita concurrencia a menos que lo necesites. Añade complejidad para debugear.
- Si fallan tareas en AsyncIO, debes manejar el rastreo de errores en corutinas (Tracebacks asíncronos).
- Multiprocessing no comparte variables globales (la memoria está aislada). Tienes que usar colas (`multiprocessing.Queue`) para pasar datos entre ellos.
"""

def cheat_sheet():
    print("""
    +-------------------+----------------------+--------------------+--------------------+
    | Herramienta       | Tipo de Tarea        | El GIL bloquea?    | Complejidad        |
    +-------------------+----------------------+--------------------+--------------------+
    | Secuencial        | Scripts simples      | Sí                 | Baja               |
    | Threading         | I/O (< 100 tareas)   | No (en I/O)        | Media              |
    | AsyncIO           | I/O Masivo (10k+)    | No (Suelta loop)   | Alta (async/await) |
    | Multiprocessing   | CPU Pesado           | No (Son procesos)  | Media-Alta         |
    +-------------------+----------------------+--------------------+--------------------+
    """)

if __name__ == "__main__":
    cheat_sheet()
