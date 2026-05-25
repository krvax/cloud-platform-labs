# 🟢 Nivel 01: Fundamentos (Foundations)

En Bridgewater, el código que escribes debe ser tan claro y estructurado como tus pensamientos. No eres el único que leerá el código; tu equipo (a las 3 AM durante un on-call) también lo hará. 

Aquí cubrimos cómo pasar de un script de un principiante a una herramienta de SRE mantenible.

## Archivos del Laboratorio

1. **`01_pep8_standards.py`**
   - **Objetivo**: Conocer el estilo oficial de Python. Escribir código feo no es solo un problema estético, genera deuda técnica y Bugs difíciles de detectar.
   - **SRE Angle**: Herramientas como `black`, `flake8` o `ruff` deben estar en tu pipeline de CI/CD para automatizar esto (Leverage).

2. **`02_type_hints.py`**
   - **Objetivo**: Introducción al tipado estático (`typing`). 
   - **SRE Angle**: En infraestructura crítica, pasar un string cuando se esperaba un diccionario puede tumbar un sistema. Los Type Hints son la "primera línea de defensa" en un entorno de Radical Transparency.

3. **`03_logging_not_print.py`**
   - **Objetivo**: Desterrar la función `print()` del código de producción.
   - **SRE Angle**: `print()` desaparece si cierras la terminal. `logging` escribe en streams (como `stdout` o archivos) con niveles de severidad (`INFO`, `WARNING`, `ERROR`), tiempos, e hilos, información crítica para Datadog/Splunk/CloudWatch.

4. **`04_context_managers.py`**
   - **Objetivo**: Manejo seguro de recursos con `with`.
   - **SRE Angle**: Dejar conexiones a base de datos abiertas o archivos sin cerrar causa "Resource Leaks". Un buen context manager asegura que los recursos se limpien *incluso si hay un Crash o Exception*.

---

### Tarea de Reflexión
Después de ejecutar estos scripts, pregúntate: *¿Si este código falla a las 3 AM y alguien más lo tiene que revisar, tendrá todo el contexto necesario?*
