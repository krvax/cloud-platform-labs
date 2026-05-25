# 🧩 Nivel 03: Patrones (Patterns)

En infraestructura crítica, las cosas fallan. Las redes se caen, las bases de datos colapsan, los límites de API (Rate Limits) se alcanzan. Un código "feliz" que asume que todo funcionará siempre no es un código SRE.

Aquí exploramos patrones de diseño arquitectónico que dotan a nuestro código de "Auto-curación" y resiliencia.

## Archivos del Laboratorio

1. **`01_decorators_retry.py`**
   - **Objetivo**: Escribir un decorador que añada lógica de reintento automático (*Exponential Backoff*) a cualquier función.
   - **SRE Angle**: Cuando AWS Throttles tus llamadas a la API de EC2 o cuando una base de datos sufre un *Failover*, el reintento evita una alerta a las 3 AM.

2. **`02_decorator_timing.py`**
   - **Objetivo**: Inyectar telemetría en nuestro código para saber cuánto tarda una función en ejecutarse.
   - **SRE Angle**: Profiling y SLIs (Service Level Indicators). Sin medir el tiempo de ejecución de las transacciones, no puedes establecer SLOs confiables.

3. **`03_factory_pattern.py`**
   - **Objetivo**: Abstraer la creación de objetos para facilitar el mantenimiento.
   - **SRE Angle**: Para abstraer clientes de la nube (ej. Cliente AWS, Cliente GCP) sin acoplar el resto del código a implementaciones específicas.

4. **`04_strategy_pattern.py`**
   - **Objetivo**: Encapsular algoritmos y hacerlos intercambiables en tiempo de ejecución.
   - **SRE Angle**: Diferentes estrategias de despliegue (Blue/Green, Canary, Rolling) aplicadas a un orquestador, seleccionables desde configuración sin alterar el core logic.

---

### Tarea de Reflexión
*Si pudieras inyectar un decorador de reintento a TODAS las llamadas de base de datos de tu empresa, ¿cuántos falsos positivos de PagerDuty evitarías por mes?*
