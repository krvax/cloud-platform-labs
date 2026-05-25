# 📊 Nivel 02: Estructuras de Datos (Data Structures)

Para un SRE de élite, la memoria RAM es un recurso limitado. Si tienes que parsear un log de VPC de 150GB, no puedes meterlo todo en una lista en memoria. 

Aquí aprenderás a usar estructuras de datos eficientes para manipular volúmenes masivos de información de forma elegante y limpia, logrando el máximo "Leverage".

## Archivos del Laboratorio

1. **`01_generators_yield.py`**
   - **Objetivo**: Leer flujos infinitos o masivos de datos usando un consumo de memoria constante de `O(1)`.
   - **SRE Angle**: Parseo de Access Logs de Nginx, CloudTrail logs, o volcado masivo de S3 sin recibir un Out Of Memory (OOM) Kill en tu Pod de K8s.

2. **`02_collections_module.py`**
   - **Objetivo**: Dejar de reinventar la rueda con diccionarios y listas estándar. Conocer `defaultdict`, `Counter` y `deque`.
   - **SRE Angle**: Para contar IPs baneadas, rastrear latencias en una ventana de tiempo, o agrupar errores rápidamente, la librería estándar ya tiene herramientas optimizadas en C.

3. **`03_dataclasses.py`**
   - **Objetivo**: Crear objetos ligeros para transportar datos sin tener que escribir `__init__`, `__repr__` o `__eq__` a mano.
   - **SRE Angle**: Cuando extraes métricas de una API (ej. Datadog o Prometheus) y necesitas estructurarlas antes de enviarlas a una base de datos o mostrarlas en un CLI.

---
### Tarea de Reflexión
*Piensa en el script más pesado o lento que has escrito. ¿Cómo podrías haber reducido la huella de memoria usando un Generador en lugar de una Lista?*
