"""
NIVEL 5: Testing Infra SRE con Moto (Mocking)

Nunca pruebes scripts destructivos contra AWS real en desarrollo.
`moto` intercepta las llamadas de Boto3 a nivel de red y crea un AWS "falso" en la RAM local.

Bridgewater Angle: Defensive Engineering. "Confía, pero verifica (con tests automatizados)".
En un pipeline CI/CD, este test asegura que no corrompiste la lógica de auto-scaling.
"""

import boto3
import pytest
from moto import mock_aws

# --- EL CÓDIGO DE PRODUCCIÓN (Lo que probaríamos) ---
def clean_unused_ebs_volumes(region_name="us-east-1"):
    """
    Busca volúmenes EBS en estado 'available' (no atachados) y los borra para ahorrar dinero.
    """
    ec2 = boto3.client('ec2', region_name=region_name)
    deleted_count = 0
    
    # Usamos paginator como SREs de verdad (Nivel 5.1)
    paginator = ec2.get_paginator('describe_volumes')
    
    for page in paginator.paginate(Filters=[{'Name': 'status', 'Values': ['available']}]):
        for vol in page.get('Volumes', []):
            vol_id = vol['VolumeId']
            ec2.delete_volume(VolumeId=vol_id)
            deleted_count += 1
            
    return deleted_count


# --- EL TEST SRE (Usando pytest y moto) ---

@mock_aws
def test_clean_unused_ebs_volumes():
    """
    Al usar el decorador @mock_aws, CUALQUIER llamada de boto3 aquí dentro
    se intercepta y NO va a la cuenta real de AWS.
    """
    # 1. SETUP (Arrange): Preparamos el entorno falso en moto
    ec2 = boto3.client('ec2', region_name='us-east-1')
    
    # Creamos un volumen "en uso" (No debería borrarse)
    ec2.create_volume(AvailabilityZone='us-east-1a', Size=10, VolumeType='gp2') # Por defecto se crea en available
    # No podemos atacharlo fácilmente sin crear instancia, así que crearemos dos volúmenes,
    # y asumiremos que queremos borrar los 'available'. Por defecto moto los crea como 'available'.
    
    # Crearemos 3 volúmenes
    ec2.create_volume(AvailabilityZone='us-east-1a', Size=20, VolumeType='gp2')
    ec2.create_volume(AvailabilityZone='us-east-1a', Size=30, VolumeType='gp2')
    
    # Verificamos que hay 3 creados en nuestro AWS falso
    vols_before = ec2.describe_volumes()['Volumes']
    assert len(vols_before) == 3
    
    # 2. ACT: Ejecutamos nuestro script destructor
    deleted = clean_unused_ebs_volumes(region_name='us-east-1')
    
    # 3. ASSERT: Verificamos resultados
    assert deleted == 3
    
    vols_after = ec2.describe_volumes()['Volumes']
    assert len(vols_after) == 0

if __name__ == "__main__":
    print("Para correr este test, ejecuta en la terminal:")
    print("pytest 03_mock_testing_moto.py -v")
