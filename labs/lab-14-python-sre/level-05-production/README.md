# 🚀 Nivel 05: Producción (Production)

Llegaste al último nivel. Aquí es donde los scripts se convierten en herramientas de plataforma.
En Bridgewater, no vas a escribir scripts que corran solo en tu laptop; escribirás automatización interactuando con la Nube (AWS), creando CLIs profesionales y, lo más importante: **Pruebas (Testing) rigurosas**.

## Archivos del Laboratorio

1. **`01_boto3_auditor.py`**
   - **Objetivo**: Uso de Boto3 (SDK de AWS) y Paginadores para auditar recursos sin ahogarse en APIs grandes.
   - **SRE Angle**: ¿Cómo listas miles de instancias EC2 sin agotar la memoria ni alcanzar un Rate Limit? Paginations.

2. **`02_incident_cli.py`**
   - **Objetivo**: Escribir una interfaz de línea de comandos (CLI) real usando `argparse`.
   - **SRE Angle**: Darle "Leverage" a tu equipo de On-Call. En lugar de que corran comandos oscuros de Bash o copien scripts sueltos, creas un CLI interno (`sre-tool get-logs --env prod`).

3. **`03_mock_testing_moto.py`**
   - **Objetivo**: Cómo probar código que borra instancias de AWS... *sin borrar instancias reales*. (Usando la librería `moto`).
   - **SRE Angle**: Defensa (Defensive Engineering). Nadie despliega un script que manipula Infra sin probarlo primero en un entorno Mock de AWS simulado en memoria.

4. **`04_health_checker.py`**
   - **Objetivo**: Un mini demonio (Daemon) que revisa la salud de endpoints y usa asincronía y logging. Es un proyecto de graduación.
   - **SRE Angle**: Tu propio *Pingdom* o *Datadog Synthetics* en miniatura, construido con código SRE sólido.

---
### Tarea de Reflexión Final
*¿Puedes combinar el AsyncIO del Nivel 4, el Dataclass del Nivel 2 y los Decoradores del Nivel 3 para crear una herramienta de auditoría de AWS ultra rápida que reporte en un JSON estructurado?*
