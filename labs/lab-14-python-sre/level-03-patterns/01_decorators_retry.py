"""
NIVEL 3: Decorators - Exponential Backoff Retry

En entornos cloud, el "Transient Failure" (fallo temporal) es la norma.
Un decorador nos permite inyectar lógica de reintento "alrededor" de una función
sin tener que modificar la lógica de negocio de la propia función.

Bridgewater Angle: Resiliencia automatizada. La automatización debe ser defensiva.
"""

import time
import random
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Definimos el decorador
def retry_with_backoff(max_retries: int = 3, initial_delay: float = 1.0, backoff_factor: float = 2.0):
    """
    Reintenta la ejecución si la función lanza una excepción.
    Aumenta el tiempo de espera exponencialmente en cada reintento.
    """
    def decorator(func):
        @wraps(func) # Preserva el nombre y docstring de la función original
        def wrapper(*args, **kwargs):
            delay = initial_delay
            for attempt in range(1, max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_retries:
                        logger.error(f"❌ Fallo definitivo tras {max_retries} intentos: {e}")
                        raise
                    
                    logger.warning(f"⚠️ Intento {attempt} falló ({e}). Reintentando en {delay}s...")
                    time.sleep(delay)
                    delay *= backoff_factor # Aumentamos la espera (Exponential Backoff)
        return wrapper
    return decorator

# Función SRE protegida
@retry_with_backoff(max_retries=4, initial_delay=0.5, backoff_factor=1.5)
def call_flaky_aws_api(instance_id: str):
    """Simula una llamada a AWS que falla el 70% de las veces."""
    logger.info(f"Contactando API de AWS para {instance_id}...")
    
    if random.random() < 0.7:
        raise ConnectionError("Rate Limit Exceeded (ThrottlingException)")
        
    logger.info("✅ Llamada exitosa a la API de AWS.")
    return {"status": "success", "id": instance_id}

if __name__ == "__main__":
    logger.info("Probando función con decorador de Auto-Curación...")
    try:
        call_flaky_aws_api("i-0abc1234")
    except Exception:
        logger.error("El proceso maestro capturó el fallo final.")
