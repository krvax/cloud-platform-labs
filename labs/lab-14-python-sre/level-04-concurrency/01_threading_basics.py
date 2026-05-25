"""
NIVEL 4: Threading (I/O Bound)

Cuando una función espera algo externo (una petición HTTP, un Query a la BD, leer un archivo),
el GIL de Python se libera temporalmente.
Esto hace que `threading` sea perfecto para tareas I/O Bound.

Bridgewater Angle: Si debes hacer PING a 10 servidores, secuencialmente tardas 10x latencia.
Con Threading, tardas 1x latencia.
"""

import time
import requests # Ojo: requests es sincrónico bloqueante. Por eso usamos hilos.
from concurrent.futures import ThreadPoolExecutor

URLS = [
    "https://httpstat.us/200?sleep=1000", # Tarda 1 segundo a propósito
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
]

def check_service(url: str) -> str:
    start = time.time()
    resp = requests.get(url)
    duration = time.time() - start
    return f"[{resp.status_code}] {url} -> {duration:.2f}s"

def run_sequential():
    print("⏳ Ejecución SECUENCIAL (Lenta)")
    start = time.time()
    for url in URLS:
        print(check_service(url))
    print(f"Total: {time.time() - start:.2f}s\n")

def run_threaded():
    print("🚀 Ejecución CON THREADS (ThreadPoolExecutor)")
    start = time.time()
    
    # ThreadPoolExecutor maneja el pool de hilos automáticamente
    with ThreadPoolExecutor(max_workers=5) as executor:
        # map ejecuta la función sobre cada elemento de la lista en un hilo separado
        results = executor.map(check_service, URLS)
        
        for res in results:
            print(res)
            
    print(f"Total: {time.time() - start:.2f}s\n")

if __name__ == "__main__":
    run_sequential()  # Debería tardar ~5 segundos
    run_threaded()    # Debería tardar ~1 segundo
