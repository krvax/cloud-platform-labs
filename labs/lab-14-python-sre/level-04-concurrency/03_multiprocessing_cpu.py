"""
NIVEL 4: Multiprocessing (CPU Bound)

Si tu tarea NO espera a la red (I/O), sino que está al 100% calculando (ej. Hashear
contraseñas, machine learning, comprimir backups, procesar imágenes),
ni Threading ni AsyncIO sirven en Python debido al GIL.

La única forma de usar tus 16 Cores de CPU es usar `multiprocessing`.
Esto levanta procesos independientes de Python, cada uno con su propio GIL y Memoria.

Bridgewater Angle: Máximo throughput para procesamiento de datos pesado.
PERO, ten cuidado: crear procesos consume mucha RAM, a diferencia de los hilos.
"""

import time
import math
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor

# Función pesada en CPU (Calcula si muchos números grandes son primos)
def is_prime(n):
    if n < 2: return False
    if n == 2: return True
    if n % 2 == 0: return False
    sqrt_n = int(math.isqrt(n)) + 1
    for i in range(3, sqrt_n, 2):
        if n % i == 0:
            return False
    return True

def heavy_computation(chunk_id):
    # Simulamos calcular miles de primos grandes
    count = 0
    start_num = 10_000_000
    for i in range(start_num, start_num + 300_000):
        if is_prime(i):
            count += 1
    return f"Chunk {chunk_id}: Encontrados {count} primos."

def run_threaded():
    print("⏳ Ejecución con THREADS (Lenta por el GIL en tareas de CPU)")
    start = time.time()
    with ThreadPoolExecutor(max_workers=4) as executor:
        list(executor.map(heavy_computation, range(4)))
    print(f"Total Threads: {time.time() - start:.2f}s\n")

def run_multiprocess():
    print("🚀 Ejecución con MULTIPROCESSING (Rápida, usa todos los cores)")
    start = time.time()
    # Usa procesos nativos en vez de hilos
    with ProcessPoolExecutor(max_workers=4) as executor:
        list(executor.map(heavy_computation, range(4)))
    print(f"Total Multiprocessing: {time.time() - start:.2f}s\n")

if __name__ == "__main__":
    # Importante: Multiprocessing SIEMPRE debe correr dentro del bloque if __name__ == '__main__' en Windows.
    print("Iniciando benchmark CPU Bound...")
    # Verás que Threading incluso puede ser más lento que hacerlo secuencial por la contención del GIL.
    # Multiprocessing lo hará casi 4 veces más rápido (si tienes 4 cores).
    run_threaded()
    run_multiprocess()
