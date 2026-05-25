"""
NIVEL 5: Boto3 Auditor (Paginadores)

Cuando usas AWS, las APIs devuelven un máximo de resultados (ej. 1000 items).
Si tienes 5000 instancias EC2, la llamada `describe_instances()` solo te dará las
primeras 1000, ocultando las otras 4000. 

Los Paginadores abstraen el uso del "NextToken", permitiéndote procesar todo
de forma segura y sin consumir memoria excesiva (funcionan como Generadores de Python!).
"""

import boto3
import logging

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)

def audit_s3_buckets_naive():
    """Forma INGENUA de llamar a AWS (Si hay más de 1000 objetos, fallará o truncará)."""
    logger.warning("❌ Usando forma ingenua (Peligroso en cuentas AWS gigantes)...")
    s3 = boto3.client('s3')
    
    try:
        response = s3.list_buckets()
        logger.info(f"Encontrados {len(response.get('Buckets', []))} buckets.")
    except Exception as e:
        logger.error(f"Fallo al conectar a AWS: Verifica que tienes credenciales configuradas en tu entorno local. Error: {e}")

def audit_s3_objects_paginated(bucket_name: str):
    """Forma SRE de auditar objetos: Usando Paginators."""
    logger.info(f"✅ Usando paginadores para auditar bucket '{bucket_name}'...")
    s3 = boto3.client('s3')
    
    # Crea un paginador para la operación específica
    paginator = s3.get_paginator('list_objects_v2')
    
    # El paginador devuelve un Generador. Carga página por página bajo demanda.
    pages = paginator.paginate(Bucket=bucket_name)
    
    total_objects = 0
    total_size_bytes = 0
    
    try:
        for page in pages:
            if 'Contents' in page:
                for obj in page['Contents']:
                    total_objects += 1
                    total_size_bytes += obj['Size']
                    
        logger.info(f"Total Objetos: {total_objects}")
        logger.info(f"Tamaño Total: {total_size_bytes / 1024 / 1024:.2f} MB")
        
    except Exception as e:
         logger.error(f"Error de AWS API: {e}. (Asegúrate de que el bucket exista y tengas permisos).")

if __name__ == "__main__":
    # Importante: Esto requiere credenciales válidas en ~/.aws/credentials
    # O variables de entorno AWS_ACCESS_KEY_ID y AWS_SECRET_ACCESS_KEY.
    logger.info("Iniciando auditoría...")
    audit_s3_buckets_naive()
    
    # Ejemplo de uso:
    # audit_s3_objects_paginated("mi-bucket-de-logs-de-produccion")
