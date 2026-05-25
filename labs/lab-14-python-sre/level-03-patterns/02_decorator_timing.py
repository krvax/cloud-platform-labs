"""
NIVEL 3: Decorators - Telemetría y Timing

SRE significa medirlo todo. No podemos mejorar lo que no medimos.
Este decorador envuelve cualquier función e imprime cuánto tardó en ejecutarse.

En el mundo real, en lugar de hacer print/logging, enviaríamos este dato
a un backend como Prometheus, Datadog (StatsD) o CloudWatch.
"""

import time
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

def measure_latency(metric_name: str = None):
    """
    Decorador que mide el tiempo de ejecución (SLI) de una función.
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            start_time = time.perf_counter() # perf_counter es más preciso que time.time()
            
            result = func(*args, **kwargs)
            
            end_time = time.perf_counter()
            duration_ms = (end_time - start_time) * 1000
            
            m_name = metric_name or func.__name__
            logger.info(f"[METRIC] {m_name}_latency_ms = {duration_ms:.2f} ms")
            
            # Aquí enviaríamos a Prometheus/StatsD:
            # statsd.timing(f"function.{m_name}.latency", duration_ms)
            
            return result
        return wrapper
    return decorator

@measure_latency(metric_name="k8s_scale_up")
def scale_kubernetes_deployment(replicas: int):
    """Simula el escalado de un deployment."""
    logger.info(f"Escalando deployment a {replicas} réplicas...")
    time.sleep(1.2) # Simulamos latencia de red contra el kube-apiserver
    return True

@measure_latency() # Si no pasamos nombre, usará el nombre de la función
def fast_db_query():
    time.sleep(0.05)
    return [{"user": "jdoe"}]

if __name__ == "__main__":
    scale_kubernetes_deployment(5)
    fast_db_query()
