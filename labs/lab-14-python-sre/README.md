# 🐍 Python SRE Mastery Lab — De Menor a Mayor con Ollama

Bienvenido al laboratorio de nivel Senior para prepararte de cara a las rondas técnicas de Bridgewater y otros roles de SRE de infraestructura crítica.

Este laboratorio está diseñado para ir desde las bases sólidas (escribir código mantenible) hasta patrones de producción avanzados (concurrencia, resiliencia y pruebas).

## 🚀 Estructura del Laboratorio

1. **[Nivel 01: Fundamentos (Foundations)](./level-01-foundations/README.md)**
   Escribir código legible y mantenible: PEP8, type hints, logging, y context managers.
2. **[Nivel 02: Estructuras de Datos (Data Structures)](./level-02-data-structures/README.md)**
   El poder de `yield`, comprehensions, `collections` y `dataclasses` para procesar miles de datos sin saturar la RAM.
3. **[Nivel 03: Patrones (Patterns)](./level-03-patterns/README.md)**
   Código autocurativo: decoradores de reintento, medición de tiempos, factories y strategies.
4. **[Nivel 04: Concurrencia (Concurrency)](./level-04-concurrency/README.md)**
   El salto al performance: `threading` vs `asyncio` vs `multiprocessing`.
5. **[Nivel 05: Producción (Production)](./level-05-production/README.md)**
   Llevando todo a AWS: Auditoría con Boto3, CLI de incidentes y Mocking con `moto`.

## 🤖 El Mentor: `ollama_mentor.py`

Este laboratorio cuenta con un script interactivo en la raíz: `ollama_mentor.py`. Es un CLI interactivo conectado a tu instancia local de Ollama (ej. `llama3` o `codellama`).
Úsalo para simular preguntas de entrevista, revisar el código que escribas o que te explique conceptos en los que tengas dudas.

**Cómo usarlo:**
```bash
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el mentor
python ollama_mentor.py
```

## 🎯 Regla de Oro (SRE Mindset)
> *"I don't just solve the algorithmic problem; I build leverage with observability and error handling."*
