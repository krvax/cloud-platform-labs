"""
NIVEL 3: Strategy Pattern

El patrón Strategy es ideal cuando tienes una tarea principal, pero el "Cómo" se ejecuta
esa tarea puede cambiar dinámicamente.

Ejemplo SRE: Un orquestador de despliegues. Quieres desplegar código nuevo a K8s.
Pero la estrategia podría ser:
- Recreate (Tirar lo viejo, levantar lo nuevo - Downtime)
- RollingUpdate (Matar de a 1, levantar de a 1 - No downtime)
- BlueGreen (Levantar todo el nuevo entorno, cambiar el tráfico - Cero riesgo)

Bridgewater Angle: Intercambiabilidad. Tu orquestador central (Pipeline) se 
mantiene intacto. Solo cambias la "Estrategia" que se inyecta.
"""

from abc import ABC, abstractmethod
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# 1. Definimos la Interfaz Estrategia
class DeploymentStrategy(ABC):
    @abstractmethod
    def execute(self, target_service: str, new_version: str):
        pass

# 2. Implementamos las estrategias
class RecreateStrategy(DeploymentStrategy):
    def execute(self, target_service: str, new_version: str):
        logger.info(f"--- RECREATE: {target_service} ---")
        logger.warning(f"1. Apagando TODOS los pods de {target_service} (Downtime esperado).")
        logger.info(f"2. Desplegando versión {new_version}.")
        logger.info(f"✅ Completado.")

class RollingUpdateStrategy(DeploymentStrategy):
    def execute(self, target_service: str, new_version: str):
        logger.info(f"--- ROLLING UPDATE: {target_service} ---")
        logger.info(f"1. Iniciando actualización gradual a {new_version}...")
        logger.info(f"2. Pod V1 destruido -> Pod V2({new_version}) creado.")
        logger.info(f"✅ Completado sin downtime global.")

class BlueGreenStrategy(DeploymentStrategy):
    def execute(self, target_service: str, new_version: str):
        logger.info(f"--- BLUE/GREEN: {target_service} ---")
        logger.info(f"1. Levantando stack paralelo GREEN con {new_version}.")
        logger.info(f"2. Ejecutando tests E2E contra entorno GREEN.")
        logger.info(f"3. Cambiando ruteo en el Load Balancer (BLUE -> GREEN).")
        logger.info(f"✅ Completado.")

# 3. El Contexto (El Orquestador / Pipeline)
class DeploymentPipeline:
    def __init__(self, strategy: DeploymentStrategy):
        # Inyección de dependencia (La estrategia se inyecta)
        self._strategy = strategy

    def set_strategy(self, strategy: DeploymentStrategy):
        """Permite cambiar la estrategia en tiempo de ejecución."""
        self._strategy = strategy

    def deploy(self, service: str, version: str):
        logger.info("Iniciando Pipeline de CD SRE...")
        # Delega el algoritmo a la estrategia
        self._strategy.execute(service, version)

# ==========================================
# Ejecución
# ==========================================
if __name__ == "__main__":
    # Creamos el pipeline por defecto con RollingUpdate
    pipeline = DeploymentPipeline(RollingUpdateStrategy())
    pipeline.deploy("auth-service", "v2.0.1")
    
    print("\n" + "="*40 + "\n")
    
    # Supongamos que es el sistema de facturación. No queremos riesgos, usamos Blue/Green.
    pipeline.set_strategy(BlueGreenStrategy())
    pipeline.deploy("billing-service", "v3.5.0")
