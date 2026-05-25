"""
PASO 3: LA SOLUCIÓN — Lo que escribirías en la entrevista

Este es el código que TÚ ya escribiste (casi idéntico).
Cada línea tiene un comentario explicando QUÉ hace y POR QUÉ.

Ejecútalo y compara el tiempo con step_01.

    python step_03_async_solution.py

──────────────────────────────────────────────────────────────
ANATOMÍA LÍNEA POR LÍNEA:
──────────────────────────────────────────────────────────────
"""

import asyncio   # (1) La librería de concurrencia asíncrona de Python
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import httpx     # (2) Cliente HTTP que soporta async (requests NO soporta)
import time

# ── SERVIDOR LOCAL MOCK (SRE Approach) ──────────────────────────────────
# Levantamos un servidor local que simule la latencia de 2 segundos.
# Usamos ThreadingHTTPServer para procesar peticiones concurrentemente.
class MockHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor para mantener la consola limpia

    def do_GET(self):
        time.sleep(2.0)  # Simula 2 segundos de latencia de red
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(b'{"status": "healthy"}')

def start_local_server() -> str:
    # Port 0 le pide al Sistema Operativo cualquier puerto libre automáticamente
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_port}/health"
# ─────────────────────────────────────────────────────────────────────────


# ┌──────────────────────────────────────────────────────────┐
# │  (3) async def = define una "coroutine" (tarea async)    │
# │  No es una función normal. No se ejecuta al llamarla.    │
# │  Se "planifica" y el Event Loop la ejecutará cuando sea   │
# │  su turno.                                                │
# └──────────────────────────────────────────────────────────┘
async def check_health(client: httpx.AsyncClient, url: str) -> dict:
    """Verifica un endpoint. Retorna status o error."""
    try:
        # ┌──────────────────────────────────────────────────┐
        # │  (4) await = "suelta el control mientras espero" │
        # │  En este momento, el Event Loop puede ejecutar   │
        # │  OTRA coroutine mientras esta espera la red.     │
        # │  Es como decirle a Python: "ve a hacer otra      │
        # │  cosa, yo te aviso cuando tenga la respuesta."   │
        # └──────────────────────────────────────────────────┐
        response = await client.get(url, timeout=5.0)

        return {
            "url": url,
            "status": response.status_code,
        }

    except Exception as e:
        # (5) Si falla (timeout, DNS, etc), NO crasheamos todo.
        #     Capturamos y reportamos. El resto de checks siguen.
        return {
            "url": url,
            "error": str(e),
        }


async def main():
    print("🚀 Iniciando Servidor de Pruebas Local...")
    target_url = start_local_server()
    services = [target_url] * 5

    print("🚀 Ejecutando health check ASÍNCRONO...\n")
    start = time.time()

    # ┌──────────────────────────────────────────────────────────┐
    # │  (6) async with = Context Manager asíncrono.             │
    # │  httpx.AsyncClient() abre un "connection pool" (grupo    │
    # │  de conexiones reutilizables). Al salir del `with`,      │
    # │  cierra todas las conexiones limpiamente.                │
    # └──────────────────────────────────────────────────────────┘
    async with httpx.AsyncClient() as client:

        # ┌──────────────────────────────────────────────────────┐
        # │  (7) List comprehension que crea las "promesas".     │
        # │  IMPORTANTE: Aquí NO se ejecuta nada todavía.        │
        # │  Solo estamos creando una lista de coroutines.       │
        # └──────────────────────────────────────────────────────┘
        tasks = [check_health(client, url) for url in services]

        # ┌──────────────────────────────────────────────────────┐
        # │  (8) asyncio.gather(*tasks) = "ENVÍA TODO A LA VEZ" │
        # │  El * desempaqueta la lista.                         │
        # │  gather() ejecuta TODAS las coroutines               │
        # │  concurrentemente y espera a que TODAS terminen.     │
        # └──────────────────────────────────────────────────────┘
        results = await asyncio.gather(*tasks)

    # Mostrar resultados
    for result in results:
        if "error" in result:
            print(f"  ❌ {result['url']} -> ERROR: {result['error']}")
        else:
            print(f"  ✅ {result['url']} -> {result['status']}")

    elapsed = time.time() - start
    print(f"\n⏱️  Total: {elapsed:.2f} segundos para {len(services)} servicios")
    print(f"📊 Proyección para 200 servicios: ~{elapsed:.0f}-{elapsed*2:.0f} segundos")
    print("\n✅ De ~10 segundos a ~2 segundos. Eso es LEVERAGE.\n")


# ┌──────────────────────────────────────────────────────────────┐
# │  (9) asyncio.run() = Arranca el Event Loop principal.       │
# │  Solo se llama UNA VEZ en todo el programa.                  │
# │  Es el "motor" que ejecuta todas las coroutines.             │
# └──────────────────────────────────────────────────────────────┘
if __name__ == "__main__":
    asyncio.run(main())
