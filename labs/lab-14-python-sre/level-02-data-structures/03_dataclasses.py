"""
NIVEL 2: Dataclasses

Cuando haces scripts, a menudo tienes variables sueltas o diccionarios (`dict`) 
que pasan por muchas funciones. Esto causa errores si alguien olvida una llave.
Las clases tradicionales requieren mucho boilerplate (`__init__`).

`@dataclass` resuelve esto: clases puras de datos, fuertemente tipadas y limpias.
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List

# ❌ SIN DATACLASS (Requiere escribir mucho boilerplate)
class IncidentOld:
    def __init__(self, id: str, severity: int, affected_services: list):
        self.id = id
        self.severity = severity
        self.affected_services = affected_services
        self.timestamp = datetime.now()
        
    def __repr__(self):
        return f"IncidentOld(id={self.id}, sev={self.severity})"

# ✅ CON DATACLASS (Senior Pythonista)
@dataclass
class Incident:
    """
    Define un incidente de SRE.
    Al añadir el decorador, Python autogenera el __init__, __repr__, __eq__, etc.
    """
    id: str
    severity: int
    affected_services: List[str]
    # field(default_factory=...) asegura que cada instancia tenga su propia lista/fecha nueva
    timestamp: datetime = field(default_factory=datetime.now)
    resolved: bool = False

    def escalate(self):
        """Aumenta la severidad si es necesario (1 es lo más alto)."""
        if self.severity > 1:
            self.severity -= 1
            print(f"🚨 Incidente {self.id} escalado a severidad SEV-{self.severity}")

if __name__ == "__main__":
    # La Dataclass automáticamente provee un constructor basado en las variables declaradas
    inc_db = Incident(
        id="INC-2023-01",
        severity=3,
        affected_services=["postgresql-primary", "cache-redis"]
    )
    
    print("Impresión limpia gracias al __repr__ automático:")
    print(inc_db)
    
    print("\nAccediendo a propiedades:")
    print(f"ID: {inc_db.id} | Creado: {inc_db.timestamp}")
    
    # Lógica de la clase
    print("\nEscalando incidente...")
    inc_db.escalate()
