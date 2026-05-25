"""
NIVEL 3: Factory Pattern

SRE trata de construir herramientas que soporten abstracciones limpias.
Supongamos que hacemos un CLI para manejar alertas, pero podríamos usar PagerDuty,
OpsGenie o Slack. Si cableamos (hard-code) las llamadas HTTP por todos lados,
cambiar de proveedor será un dolor de cabeza.

El Factory Pattern centraliza la creación de estos clientes.

Bridgewater Angle: Mantenibilidad y Desacoplamiento.
"""

from abc import ABC, abstractmethod

# 1. Definimos la Interfaz "Contrato" (Abstracción)
class AlertClient(ABC):
    @abstractmethod
    def trigger_alert(self, message: str) -> bool:
        pass

# 2. Implementaciones Específicas
class PagerDutyClient(AlertClient):
    def trigger_alert(self, message: str) -> bool:
        print(f"[PagerDuty API] Triggering incident: {message}")
        return True

class SlackClient(AlertClient):
    def trigger_alert(self, message: str) -> bool:
        print(f"[Slack Webhook] Sending to #alerts channel: {message}")
        return True

class OpsGenieClient(AlertClient):
    def trigger_alert(self, message: str) -> bool:
        print(f"[OpsGenie API] Creating alert: {message}")
        return True

# 3. La Factoría
class AlertClientFactory:
    """
    Se encarga de inicializar y devolver el cliente correcto basado
    en una simple configuración (String).
    """
    @staticmethod
    def get_client(provider: str) -> AlertClient:
        provider = provider.lower()
        if provider == "pagerduty":
            return PagerDutyClient()
        elif provider == "slack":
            return SlackClient()
        elif provider == "opsgenie":
            return OpsGenieClient()
        else:
            raise ValueError(f"Proveedor de alertas no soportado: {provider}")

# ==========================================
# Uso en la lógica principal (Controller)
# ==========================================
if __name__ == "__main__":
    # Imagina que leemos esto de una variable de entorno o un config.yaml
    CONFIG_PROVIDER = "slack" 
    
    # El core de la aplicación NO sabe nada sobre APIs HTTP.
    # Solo confía en que la factoría le dará un "AlertClient" válido.
    try:
        alert_system = AlertClientFactory.get_client(CONFIG_PROVIDER)
        alert_system.trigger_alert("🔥 CPU Spike detectado en prod-db-01 (99%)")
    except ValueError as e:
        print(f"Error de configuración: {e}")
