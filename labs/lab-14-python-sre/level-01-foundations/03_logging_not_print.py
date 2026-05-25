"""
NIVEL 1: Logging vs Print

En sistemas de producción (K8s, ECS, Lambdas), un `print()` se pierde.
El módulo `logging` añade contexto crucial: timestamps, severidad, hilos y módulos.

Bridgewater Angle: Observabilidad. Un fallo silencioso es inaceptable.
Si falla a las 3 AM, Datadog/CloudWatch debe tener el contexto exacto.
"""

import logging
import sys

# ✅ SETUP SRE-LEVEL LOGGING
# Formato: [Nivel] [Timestamp] [Archivo:Línea] - Mensaje
logging.basicConfig(
    level=logging.INFO, # Por defecto filtramos DEBUG
    format='%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout), # Imprimir en stdout (ideal para Docker/K8s)
        # logging.FileHandler("app.log")   # (Opcional) Escribir a un archivo
    ]
)

# Siempre crear un logger instanciado con el nombre del módulo actual
logger = logging.getLogger(__name__)

def connect_to_database(host: str, retries: int = 3) -> bool:
    logger.info(f"Iniciando conexión a base de datos en {host}...")
    
    try:
        # Simulamos un fallo
        raise ConnectionError("Timeout al contactar DB.")
    except ConnectionError as e:
        # ERROR level: Requiere atención (dispararía PagerDuty posiblemente)
        logger.error(f"Fallo crítico en conexión a {host}. Detalle: {e}")
        return False

def clean_tmp_files():
    # DEBUG level: Información ruidosa, útil solo para desarrollo.
    logger.debug("Analizando directorio /tmp...")
    logger.info("Limpieza de temporales completada. Liberados 200MB.")

if __name__ == "__main__":
    # print("Limpiando...") # ❌ Inútil sin contexto
    
    logger.info("🛠️ Ejecutando script de mantenimiento...")
    clean_tmp_files()
    
    db_status = connect_to_database("prod-db.internal")
    if not db_status:
        logger.warning("El proceso continuará en modo degradado (sin base de datos).")
