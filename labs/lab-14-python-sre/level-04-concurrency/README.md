# ⚡ Nivel 04: Concurrencia (Concurrency)

Como SRE, tu código rara vez hará una sola cosa a la vez. Probablemente necesites:
1. Hablar con 5 APIs de Cloud al mismo tiempo.
2. Hacer ping a 1000 IPs en tu VPC.
3. Procesar un log masivo usando todos los núcleos de CPU del servidor.

Hacerlo de forma secuencial es ineficiente. Aquí aprenderás el arte de la concurrencia en Python, entendiendo cuándo usar Hilos, cuándo Asincronía y cuándo Multiprocesamiento.

## El problema principal: El GIL (Global Interpreter Lock)
Python estándar (CPython) tiene un candado que impide que múltiples hilos de Python ejecuten código de Python a la vez. Entender esto es la diferencia entre un Junior y un Senior.

## Archivos del Laboratorio

1. **`01_threading_basics.py`**
   - **Objetivo**: `threading` (ThreadPoolExecutor). Útil para "I/O Bound" (operaciones limitadas por Entrada/Salida, como llamar a una API de AWS o consultar una base de datos).
   - **SRE Angle**: Script para reiniciar 50 instancias de EC2 de forma simultánea.

2. **`02_asyncio_fundamentals.py`**
   - **Objetivo**: `asyncio`. Un solo hilo, pero muy eficiente saltando entre tareas cuando hay latencia de red.
   - **SRE Angle**: Scraping de métricas de cientos de pods en K8s o manejo de WebSockets. 

3. **`03_multiprocessing_cpu.py`**
   - **Objetivo**: `multiprocessing`. Burlar el GIL creando procesos completamente separados (cada uno con su propio intérprete Python y memoria). Útil para "CPU Bound".
   - **SRE Angle**: Comprimir o encriptar (KMS) cientos de gigabytes de backups.

4. **`04_when_to_use_what.py`**
   - **Objetivo**: Un resumen y un pequeño script de prueba que te obligue a decidir qué herramienta usar.
   
---
### Tarea de Reflexión
*Si intentas calcular números primos gigantéscos usando 100 Hilos (`threading`), ¿por qué tu programa tardará MÁS tiempo que haciéndolo secuencialmente?* (Pista: Busca "GIL contention").
