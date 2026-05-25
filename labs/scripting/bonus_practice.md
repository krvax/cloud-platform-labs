# 🎯 Bonus Practice — Additional Exercises

> Si terminaste los warm-ups y tienes tiempo extra antes de la entrevista

---

## Exercise 4: Latency Percentiles (Python, 10 min)

### Prompt
Escribe un script que calcule p50, p95, p99 de latencia de `app.log`.

**Requisitos:**
- Streaming (no cargar todo en memoria)
- Usa una lista para acumular solo latencias
- Calcula percentiles al final con `sorted()`

```python
#!/usr/bin/env python3
import json

latencies = []
with open("app.log") as f:
    for line in f:
        try:
            r = json.loads(line)
            latencies.append(r["latency_ms"])
        except (json.JSONDecodeError, KeyError):
            continue

latencies.sort()
n = len(latencies)
p50 = latencies[int(n * 0.50)]
p95 = latencies[int(n * 0.95)]
p99 = latencies[int(n * 0.99)]

print(f"p50: {p50}ms")
print(f"p95: {p95}ms")
print(f"p99: {p99}ms")
```

---

## Exercise 5: Top Error Types (Bash, 5 min)

### Prompt
One-liner que muestre los top 3 tipos de error (campo `error`) y su frecuencia.

```bash
jq -r 'select(.error != "") | .error' app.log | sort | uniq -c | sort -nr | head -3
```

**Output esperado:**
```
     52 db_timeout
     45 null_pointer
     43 upstream_502
```

---

## Exercise 6: User Activity Report (Python, 15 min)

### Prompt
Script que genere un reporte por usuario:
- Total requests
- Requests con error 5xx
- Error rate del usuario

```python
#!/usr/bin/env python3
import json
from collections import defaultdict

user_stats = defaultdict(lambda: {"total": 0, "errors": 0})

with open("app.log") as f:
    for line in f:
        try:
            r = json.loads(line)
            user = r.get("user", "unknown")
            user_stats[user]["total"] += 1
            if r.get("status", 0) >= 500:
                user_stats[user]["errors"] += 1
        except json.JSONDecodeError:
            continue

print(f"{'User':<15} {'Total':>8} {'Errors':>8} {'Error Rate':>12}")
print("-" * 50)

for user in sorted(user_stats.keys()):
    stats = user_stats[user]
    total = stats["total"]
    errors = stats["errors"]
    rate = errors / total * 100 if total > 0 else 0
    print(f"{user:<15} {total:>8} {errors:>8} {rate:>11.2f}%")
```

---

## Exercise 7: Health Check Script (Python, 15 min)

### Prompt
Script que haga health check a una lista de URLs.

```python
#!/usr/bin/env python3
import requests
import sys

URLS = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/5",
]
TIMEOUT = 2

results = []
for url in URLS:
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            status = "✅ HEALTHY"
        else:
            status = f"⚠️  UNHEALTHY ({r.status_code})"
    except requests.exceptions.Timeout:
        status = "⏱️  TIMEOUT"
    except requests.exceptions.ConnectionError:
        status = "❌ DOWN"
    results.append((url, status))

print(f"\n{'URL':<45} Status")
print("-" * 65)
for url, status in results:
    print(f"{url:<45} {status}")

# Exit 1 si alguno no está healthy
all_ok = all("HEALTHY" in s for _, s in results)
sys.exit(0 if all_ok else 1)
```

---

## Exercise 8: Disk Usage Analyzer (Bash, 10 min)

### Prompt
Script que encuentre:
1. Top 5 directorios más grandes en `/var/log`
2. Archivos mayores a 100MB
3. Archivos borrados pero aún abiertos

```bash
#!/bin/bash

echo "=== Top 5 directorios en /var/log ==="
du -h --max-depth=1 /var/log 2>/dev/null | sort -rh | head -5

echo ""
echo "=== Archivos > 100MB ==="
find /var/log -type f -size +100M -exec ls -lh {} \; 2>/dev/null

echo ""
echo "=== Archivos borrados pero aún abiertos ==="
lsof +L1 2>/dev/null | grep deleted | head -10
```

---

## Exercise 9: K8s Pod Resource Check (Bash, 10 min)

### Prompt
Script que verifique si todos los pods en un namespace tienen `resources.requests` definidos.

```bash
#!/bin/bash

NAMESPACE=${1:-default}

echo "Checking pods in namespace: $NAMESPACE"
echo ""

kubectl get pods -n "$NAMESPACE" -o json | \
  jq -r '.items[] | 
    .metadata.name as $pod | 
    .spec.containers[] | 
    select(.resources.requests == null) | 
    "\($pod) / \(.name) — MISSING resources.requests"'

if [ $? -eq 0 ]; then
    echo "✅ All pods have resources.requests defined"
else
    echo "❌ Some pods missing resources.requests"
    exit 1
fi
```

---

## Exercise 10: AWS S3 Bucket Audit (Bash, 15 min)

### Prompt
Script que liste todos los buckets S3 y muestre:
- Nombre del bucket
- Cantidad de objetos
- Tamaño total
- Si tiene encryption habilitado

```bash
#!/bin/bash

echo "Bucket,Objects,Size,Encryption"

for bucket in $(aws s3 ls | awk '{print $3}'); do
    # Contar objetos y tamaño
    summary=$(aws s3 ls "s3://$bucket" --recursive --summarize 2>/dev/null | tail -2)
    objects=$(echo "$summary" | grep "Total Objects" | awk '{print $3}')
    size=$(echo "$summary" | grep "Total Size" | awk '{print $3}')
    
    # Verificar encryption
    enc=$(aws s3api get-bucket-encryption --bucket "$bucket" 2>&1)
    if echo "$enc" | grep -q "ServerSideEncryptionConfigurationNotFoundError"; then
        encryption="NO"
    else
        encryption="YES"
    fi
    
    echo "$bucket,$objects,$size,$encryption"
done
```

---

## Exercise 11: Log Correlation (Python, 20 min)

### Prompt
Script que dado un `request_id`, muestre toda la información relacionada.

```python
#!/usr/bin/env python3
import json
import sys

if len(sys.argv) < 2:
    print("Usage: python correlate.py <request_id>")
    sys.exit(1)

target_id = sys.argv[1]
matches = []

with open("app.log") as f:
    for line in f:
        try:
            r = json.loads(line)
            if r.get("request_id") == target_id:
                matches.append(r)
        except json.JSONDecodeError:
            continue

if not matches:
    print(f"No records found for request_id: {target_id}")
    sys.exit(1)

print(f"\n=== Request Trace: {target_id} ===\n")
for r in matches:
    print(f"[{r['ts']}] {r['level']} — {r['method']} {r['endpoint']}")
    print(f"  Status: {r['status']} | Latency: {r['latency_ms']}ms | User: {r['user']}")
    if r.get("error"):
        print(f"  Error: {r['error']}")
    print()
```

---

## Exercise 12: SLO Burn Rate Alert (Python, 25 min)

### Prompt
Script que calcule el burn rate de error budget y alerte si está en riesgo.

**Concepto:**
- SLO: 99.5% availability
- Error budget: 0.5% (30 min en 100 horas)
- Burn rate: qué tan rápido se consume el budget
- Burn rate > 1 = consumiendo más rápido de lo permitido

```python
#!/usr/bin/env python3
import json
from datetime import datetime, timedelta

SLO = 99.5
WINDOW_MINUTES = 60  # ventana de análisis

# Leer últimos N minutos
now = datetime.now()
cutoff = now - timedelta(minutes=WINDOW_MINUTES)

total = 0
errors = 0

with open("app.log") as f:
    for line in f:
        try:
            r = json.loads(line)
            ts = datetime.fromisoformat(r["ts"].replace("Z", "+00:00"))
            
            if ts >= cutoff:
                total += 1
                if r.get("status", 0) >= 500:
                    errors += 1
        except (json.JSONDecodeError, KeyError, ValueError):
            continue

if total == 0:
    print("No data in time window")
    exit(0)

error_rate = errors / total * 100
availability = 100 - error_rate
error_budget = 100 - SLO  # 0.5%

# Burn rate: cuánto del budget se consume por hora
burn_rate = error_rate / error_budget

print(f"=== SLO Burn Rate Analysis ===")
print(f"Window: last {WINDOW_MINUTES} minutes")
print(f"Total requests: {total}")
print(f"Errors: {errors}")
print(f"Error rate: {error_rate:.3f}%")
print(f"Availability: {availability:.3f}%")
print(f"SLO target: {SLO}%")
print(f"Error budget: {error_budget}%")
print(f"Burn rate: {burn_rate:.2f}x")
print()

if burn_rate > 10:
    print("🚨 CRITICAL: Burn rate > 10x — error budget will exhaust in < 6 hours")
    exit(2)
elif burn_rate > 5:
    print("⚠️  WARNING: Burn rate > 5x — error budget at risk")
    exit(1)
elif burn_rate > 1:
    print("⚡ NOTICE: Burn rate > 1x — consuming budget faster than allowed")
    exit(0)
else:
    print("✅ OK: Burn rate < 1x — within budget")
    exit(0)
```

---

## Tips para Practicar

1. **Cronométrate** — simula presión de entrevista
2. **No copies y pegues** — escribe de memoria
3. **Piensa en voz alta** — practica explicar tu razonamiento
4. **Prueba edge cases** — archivo vacío, JSON inválido, etc.

---

## Conceptos Avanzados (Si Te Preguntan)

### Reservoir Sampling
```python
import random

class ReservoirSampler:
    def __init__(self, size):
        self.size = size
        self.reservoir = []
        self.count = 0
    
    def add(self, value):
        self.count += 1
        if len(self.reservoir) < self.size:
            self.reservoir.append(value)
        else:
            j = random.randint(0, self.count - 1)
            if j < self.size:
                self.reservoir[j] = value
    
    def percentile(self, p):
        s = sorted(self.reservoir)
        return s[int(len(s) * p / 100)]
```

**Uso:** Calcular percentiles en streaming sin guardar todos los valores.

### Exponential Backoff
```python
import time

def retry_with_backoff(func, max_retries=3):
    for i in range(max_retries):
        try:
            return func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            wait = 2 ** i  # 1s, 2s, 4s
            print(f"Retry {i+1}/{max_retries} after {wait}s")
            time.sleep(wait)
```

### Rate Limiting
```python
import time

class RateLimiter:
    def __init__(self, max_calls, period):
        self.max_calls = max_calls
        self.period = period
        self.calls = []
    
    def allow(self):
        now = time.time()
        self.calls = [c for c in self.calls if now - c < self.period]
        if len(self.calls) < self.max_calls:
            self.calls.append(now)
            return True
        return False
```

---

**¡Sigue practicando!** 🚀
