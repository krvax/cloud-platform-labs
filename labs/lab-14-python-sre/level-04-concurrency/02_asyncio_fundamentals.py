"""
NIVEL 4: AsyncIO (Event Loop)

En lugar de usar recursos del Sistema Operativo para crear Hilos (pesados),
AsyncIO usa un Event Loop en UN SOLO HILO.
Cuando una función (coroutine) hace algo de red (`await`), "suelta el control"
del loop para que otra tarea corra mientras los datos llegan por la red.

Bridgewater Angle: Escala a miles de conexiones simultáneas. Threading moriría 
si intentas crear 10,000 hilos, pero AsyncIO maneja 10,000 websockets fácilmente.
"""

import asyncio
import httpx # Necesitamos librerías asíncronas, requests no funciona aquí
import time

URLS = [
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
    "https://httpstat.us/200?sleep=1000",
]

# La palabra clave 'async' define una Coroutine (promesa)
async def check_service_async(url: str, client: httpx.AsyncClient) -> str:
    start = time.time()
    
    # 'await' cede el control del Event Loop mientras esperamos el GET
    resp = await client.get(url) 
    
    duration = time.time() - start
    return f"[{resp.status_code}] {url} -> {duration:.2f}s"

async def main():
    print("🚀 Ejecución ASÍNCRONA (AsyncIO)")
    start = time.time()
    
    # Usamos un solo cliente (connection pool) para eficiencia
    async with httpx.AsyncClient() as client:
        # Creamos las tareas (aún no se ejecutan, solo se planifican)
        tasks = [check_service_async(url, client) for url in URLS]
        
        # asyncio.gather dispara todas las tareas a la vez en el Event Loop
        results = await asyncio.gather(*tasks)
        
        for res in results:
            print(res)
            
    print(f"Total: {time.time() - start:.2f}s\n")

if __name__ == "__main__":
    # Necesitamos asyncio.run() para iniciar el Event Loop principal
    asyncio.run(main())
