# Lab 15 — Python SRE Practice (Bridgewater Prep)

Ejercicios prácticos de Python enfocados en SRE para la Project Interview de Bridgewater.

## Ejercicios

| # | Archivo | Tema | Dificultad |
|---|---|---|---|
| 1 | `ex01_log_analyzer.py` | Parsing de logs + top errores por endpoint | ⭐⭐ |
| 2 | `ex02_ip_analyzer.py` | Top IPs sospechosas + endpoints que atacan | ⭐⭐ |

## Ejercicio 2 — IP Analyzer (hazlo tú)

**Escenario:** Sospechas que los errores 5xx vienen de unas pocas IPs (bad actor o cliente roto). Escribe un script que encuentre las top 10 IPs con más errores y muestre qué endpoints están atacando.

**Output esperado:**
```
🚨 TOP 10 SUSPICIOUS IPs

192.168.1.7 — 23 errors
  /api/auth/login : 15
  /api/users : 8

192.168.1.13 — 19 errors
  /api/products : 12
  /api/search : 7
```

**Pasos:**
1. Crear `ex02_ip_analyzer.py`
2. Imports: `re`, `Counter`, `defaultdict`
3. Estructura de datos: un dict de IPs donde cada value es un Counter de endpoints
4. Loop: abrir `sample_access.log`, parsear cada línea, si es error (4xx o 5xx) → agregar
5. Output: ordenar IPs por total de errores, tomar top 10, imprimir con sus endpoints

**Pista clave:**
```python
from collections import defaultdict, Counter
ip_errors = defaultdict(Counter)
# Uso: ip_errors["192.168.1.7"]["/api/login"] += 1
```

**Para parsear:** Puedes reusar el regex del ex01 o usar `split()` (más simple):
```python
parts = line.split('"')
ip = parts[0].split()[0]
endpoint = parts[1].split()[1]
status = int(parts[2].strip().split()[0])
```

## Cómo correr

```bash
cd labs/lab-15-python-sre-practice
python ex01_log_analyzer.py
```

## Approach de entrevista

1. **Clarifica** — pregunta formato del log, qué significa "last hour", output esperado
2. **Planea en voz alta** — "voy a leer línea por línea, parsear con regex, filtrar por tiempo, contar por endpoint"
3. **Empieza simple** — solución naive que funcione
4. **Optimiza si preguntan** — generators, multiprocessing, etc.
5. **Edge cases** — archivo vacío, líneas malformadas, timezone
