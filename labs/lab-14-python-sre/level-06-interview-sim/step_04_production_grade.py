"""
PASO 4: VERSIÓN PRODUCCIÓN — Lo que te diferencia de un Mid-level

Después de resolver el problema básico (step_03), el entrevistador 
preguntará: "What else would you add for production?"

Aquí agregas las 4 capas que gritan "Senior SRE":
  1. Semaphore     → Control de concurrencia (no saturar la red)
  2. Logging       → Observabilidad (no print)
  3. Dataclass     → Datos estructurados (no dicts sueltos)
  4. Retry         → Resiliencia (reintentar fallos transitorios)

    python step_04_production_grade.py

──────────────────────────────────────────────────────────────
"""

import asyncio
import asyncio
import httpx
import logging
import time
import threading
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
from dataclasses import dataclass, field
from datetime import datetime
from typing import List

# ── SERVIDOR LOCAL MOCK (SRE Approach) ──────────────────────────────────
# Levantamos un servidor local que simule endpoints saludables, con errores y latencia.
# Usamos ThreadingHTTPServer para procesar peticiones concurrentemente.
class MockHTTPHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass  # Silenciar logs del servidor para mantener la consola limpia

    def do_GET(self):
        # Simular diferentes respuestas según la URL
        if "500" in self.path:
            time.sleep(0.5)
            self.send_response(500)
            self.end_headers()
            self.wfile.write(b'Internal Server Error')
        elif "404" in self.path:
            time.sleep(0.5)
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')
        else:
            time.sleep(1.0)  # Latencia de 1 segundo
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.end_headers()
            self.wfile.write(b'{"status": "healthy"}')

def start_local_server() -> str:
    server = ThreadingHTTPServer(("127.0.0.1", 0), MockHTTPHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return f"http://127.0.0.1:{server.server_port}"
# ─────────────────────────────────────────────────────────────────────────

# ──────────────────────────────────────────────────────────────
# CAPA 1: LOGGING (No print — observable en Datadog/CloudWatch)
# ──────────────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────────────────────
# CAPA 2: DATACLASS (Datos tipados, no dicts anónimos)
# ──────────────────────────────────────────────────────────────
@dataclass
class HealthResult:
    """Resultado estructurado de un health check."""
    url: str
    status_code: int
    latency_ms: float
    is_healthy: bool
    error: str = ""
    timestamp: datetime = field(default_factory=datetime.now)


# ──────────────────────────────────────────────────────────────
# CAPA 3: SEMAPHORE (No lanzar 200 requests de golpe)
# ──────────────────────────────────────────────────────────────
MAX_CONCURRENT = 50  # Máximo 50 requests simultáneos


async def check_health(
    client: httpx.AsyncClient,
    url: str,
    semaphore: asyncio.Semaphore,
    max_retries: int = 2,
) -> HealthResult:
    """Health check con control de concurrencia y retries."""

    # ┌─────────────────────────────────────────────────────┐
    # │ async with semaphore:                                │
    # │ Solo permite MAX_CONCURRENT coroutines aquí dentro   │
    # │ al mismo tiempo. Las demás ESPERAN su turno.         │
    # └─────────────────────────────────────────────────────┘
    async with semaphore:

        # ──────────────────────────────────────────────────
        # CAPA 4: RETRY (Reintentar fallos transitorios)
        # ──────────────────────────────────────────────────
        for attempt in range(1, max_retries + 1):
            start = time.time()
            try:
                response = await client.get(url, timeout=5.0)
                latency = (time.time() - start) * 1000

                is_ok = 200 <= response.status_code < 300

                return HealthResult(
                    url=url,
                    status_code=response.status_code,
                    latency_ms=round(latency, 1),
                    is_healthy=is_ok,
                )

            except Exception as e:
                latency = (time.time() - start) * 1000

                if attempt < max_retries:
                    logger.warning(
                        f"Intento {attempt} falló para {url}: {e}. Reintentando..."
                    )
                    await asyncio.sleep(0.5 * attempt)  # Backoff simple
                else:
                    logger.error(f"Fallo definitivo para {url}: {e}")
                    return HealthResult(
                        url=url,
                        status_code=0,
                        latency_ms=round(latency, 1),
                        is_healthy=False,
                        error=str(e),
                    )


async def monitor_fleet(urls: List[str]):
    """Orquestador principal del health check."""
    logger.info(f"Iniciando auditoría de {len(urls)} endpoints...")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT)

    async with httpx.AsyncClient() as client:
        tasks = [check_health(client, url, semaphore) for url in urls]
        results: List[HealthResult] = await asyncio.gather(*tasks)

    # ── Reporte final ────────────────────────────────────
    healthy = [r for r in results if r.is_healthy]
    unhealthy = [r for r in results if not r.is_healthy]

    logger.info("─── REPORTE FINAL ───")
    for r in results:
        icon = "✅" if r.is_healthy else "❌"
        logger.info(f"{icon} {r.url} | HTTP {r.status_code} | {r.latency_ms}ms")

    logger.info(f"Saludables: {len(healthy)}/{len(results)}")

    if unhealthy:
        logger.error(
            f"🚨 ALERTA: {len(unhealthy)} servicios caídos. "
            f"Servicios: {[r.url for r in unhealthy]}"
        )

    return results


if __name__ == "__main__":
    print("🚀 Iniciando Servidor de Pruebas Local...")
    base_url = start_local_server()

    TARGETS = [
        f"{base_url}/200",  # OK (1 seg latencia)
        f"{base_url}/200",  # OK
        f"{base_url}/500",  # Server Error (500)
        f"{base_url}/200",  # OK
        f"{base_url}/404",  # Not Found (404)
    ]

    start = time.time()
    asyncio.run(monitor_fleet(TARGETS))
    elapsed = time.time() - start

    print(f"\n⏱️  Ejecución total: {elapsed:.2f}s")
    print("📊 Con Semaphore + Retry + Logging + Dataclass = Production Grade SRE")
