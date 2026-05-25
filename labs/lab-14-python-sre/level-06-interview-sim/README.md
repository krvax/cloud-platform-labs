# 🎯 Nivel 06: Simulación de Entrevista — Async Health Checker

Este nivel es diferente. No lees código — lo **construyes tú** paso a paso, exactamente como lo harías en una entrevista de Bridgewater.

## El Escenario (Tal como te lo dirían en la entrevista)

> *"We have a monitoring script that checks the health of 200 microservices.
> It currently takes 10 minutes to complete. The team is complaining.
> How would you fix it?"*

## Archivos del Laboratorio

Cada archivo es un **paso incremental**. Ejecútalos en orden.

1. **`step_01_the_problem.py`** — El script roto. Secuencial. Lento.
2. **`step_02_explain_why.py`** — Diagnóstico: ¿POR QUÉ es lento?
3. **`step_03_async_solution.py`** — Tu solución async (lo que escribirías en entrevista).
4. **`step_04_production_grade.py`** — Versión producción: Semaphore + Logging + Dataclass.

## Cómo usarlo

```bash
# Instalar dependencia (si no la tienes)
pip install httpx

# Ejecutar cada paso
python step_01_the_problem.py
python step_02_explain_why.py
python step_03_async_solution.py
python step_04_production_grade.py
```

## 🎯 Regla de Oro
> *"Don't memorize the code. Understand the WHY behind each line."*
