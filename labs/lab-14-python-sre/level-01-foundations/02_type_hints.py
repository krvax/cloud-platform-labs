"""
NIVEL 1: Type Hints (Tipado Estático)

Los Type Hints (`typing`) fueron introducidos en Python 3.5+.
En el mundo de infraestructura, pasar un string en lugar de un entero puede 
costar miles de dólares o causar un outage.

Bridgewater Angle: Reduce la ambigüedad (Truth). Permite a los IDEs y a mypy
detectar errores ANTES de ir a producción.
"""

from typing import List, Dict, Optional, Union

# ❌ SIN TIPOS (Difícil saber qué espera la función)
def terminate_instances(instance_ids, force):
    pass 

# ✅ CON TIPOS (Documentación viva y verificable)
def terminate_aws_instances(instance_ids: List[str], force: bool = False) -> bool:
    """
    Termina instancias de EC2 de manera controlada.
    
    El type hint 'List[str]' deja claro que esperamos una lista de IDs (strings).
    '-> bool' indica que retornaremos un valor booleano indicando el éxito de la operación.
    """
    print(f"Terminando instancias: {instance_ids}")
    # Lógica de terminación (boto3)
    return True

def get_instance_metadata(instance_id: str) -> Optional[Dict[str, Union[str, int]]]:
    """
    El tipo 'Optional' indica que puede retornar None (ej. si la instancia no existe).
    'Union' permite que los valores del diccionario sean str o int.
    """
    if not instance_id:
        return None
        
    return {
        "id": instance_id,
        "uptime_hours": 120,
        "state": "running"
    }

if __name__ == "__main__":
    success: bool = terminate_aws_instances(["i-1234567890abcdef0", "i-0987654321fedcba0"], force=True)
    
    metadata = get_instance_metadata("i-1234567890abcdef0")
    if metadata:
        print(f"Instancia {metadata['id']} estado: {metadata['state']}")
