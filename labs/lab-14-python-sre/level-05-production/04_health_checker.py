"""
NIVEL 5 (PROYECTO FINAL): Health Checker Asíncrono

Este script combina:
1. Concurrencia masiva (AsyncIO - Nivel 4)
2. Dataclasses para estructurar los datos (Nivel 2)
3. Logging SRE-ready (Nivel 1)
4. Patrón Retry/Error Handling implícito (Nivel 3)

Bridgewater Angle: Crea tu propio "Datadog Synthetics" local. Puede correr
como un CronJob en Kubernetes, monitoreando 50 endpoints en menos de 1 segundo.
"""

import asyncio
import httpx
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import List

# Setup Logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Estructura de Datos (Dataclass)
@dataclass
class HealthStatus:
    url: str
    status_code: int
    latency_ms: float
    timestamp: datetime = datetime.now()
    is_healthy: bool = False

async def check_endpoint(client: httpx.AsyncClient, url: str) -> HealthStatus:
    """Verifica un solo endpoint."""
    start = asyncio.get_event_loop().time()
    try:
        # Timeout agresivo (SRE mindset: no te quedes colgado esperando)
        response = await client.get(url, timeout=3.0)
        latency = (asyncio.get_event_loop().time() - start) * 1000
        
        is_ok = 200 <= response.status_code < 300
        
        return HealthStatus(
            url=url,
            status_code=response.status_code,
            latency_ms=latency,
            is_healthy=is_ok
        )
    except httpx.RequestError as e:
        logger.error(f"Fallo de conexión crítico hacia {url}: {e}")
        return HealthStatus(
            url=url,
            status_code=000,
            latency_ms=0,
            is_healthy=False
        )

async def monitor_fleet(urls: List[str]):
    """Corutina principal que orquesta los chequeos concurrentes."""
    logger.info(f"Iniciando auditoría de flota: {len(urls)} endpoints...")
    
    # Context Manager asíncrono
    async with httpx.AsyncClient() as client:
        # List Comprehension para crear las promesas
        tasks = [check_endpoint(client, url) for url in urls]
        
        # Ejecución concurrente
        results: List[HealthStatus] = await asyncio.gather(*tasks)
        
        # Procesamiento final
        unhealthy = [res for res in results if not res.is_healthy]
        
        logger.info("--- REPORTE FINAL ---")
        for res in results:
            icon = "✅" if res.is_healthy else "❌"
            logger.info(f"{icon} {res.url} | Código: {res.status_code} | Latencia: {res.latency_ms:.1f}ms")
            
        if unhealthy:
            logger.error(f"¡ALERTA! {len(unhealthy)} servicios están caídos. Lanzando PagerDuty...")
        else:
            logger.info("Flota 100% Saludable.")

if __name__ == "__main__":
    TARGETS = [
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/200",
        "https://httpbin.org/status/500", # Simulamos una caída (Internal Server Error)
        "https://httpbin.org/status/404",
        "https://httpbin.org/delay/2",    # Lento
    ]
    
    # Arrancamos el Event Loop
    asyncio.run(monitor_fleet(TARGETS))
