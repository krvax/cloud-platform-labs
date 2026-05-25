"""
NIVEL 2: Generadores y la palabra clave 'yield'

Cuando lees un archivo log de 50GB, hacer `lines = file.readlines()` cargará
50GB en la RAM. Tu proceso morirá instantáneamente por OOM (Out Of Memory).

La solución es 'yield'. Un generador procesa los elementos UNO POR UNO, 
manteniendo la memoria consumida plana O(1).
"""

import sys
import time

# ❌ FORMA INCORRECTA: Carga todo en memoria
def get_all_logs(num_lines: int):
    logs = []
    for i in range(num_lines):
        logs.append(f"INFO: Conexión aceptada desde IP 192.168.1.{i % 255}")
    return logs

# ✅ FORMA CORRECTA (SRE): Generador (Lazy evaluation)
def generate_logs(num_lines: int):
    for i in range(num_lines):
        # 'yield' pausa la función y entrega el valor. La próxima vez
        # que se pida un valor, reanudará desde aquí.
        yield f"INFO: Conexión aceptada desde IP 192.168.1.{i % 255}"

if __name__ == "__main__":
    TOTAL_LINES = 1_000_000  # 1 millón de líneas (Simulando un archivo grande)
    
    print("⏳ Probando enfoque tradicional (Lista)...")
    start = time.time()
    # Esto consumirá mucha memoria (~50-100MB solo en strings cortos)
    lista_logs = get_all_logs(TOTAL_LINES)
    print(f"Lista creada en {time.time() - start:.2f}s. Tamaño en memoria: {sys.getsizeof(lista_logs) / 1024 / 1024:.2f} MB")
    
    del lista_logs # Limpiamos RAM
    
    print("\n⏳ Probando enfoque SRE (Generador)...")
    start = time.time()
    # Esto es casi instantáneo, porque NO evalúa ni guarda el millón de strings aún.
    generador_logs = generate_logs(TOTAL_LINES)
    print(f"Generador creado en {time.time() - start:.4f}s. Tamaño en memoria: {sys.getsizeof(generador_logs)} BYTES")
    
    # Podemos iterar el generador de manera segura (simulamos procesar 5 líneas nada más para la demo)
    print("\nPrimeras 5 líneas extraídas bajo demanda:")
    for _ in range(5):
        print(next(generador_logs))
