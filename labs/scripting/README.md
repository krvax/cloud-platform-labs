# Lab: Scripting & Coding Prep

> Ejercicios prácticos para la prueba de scripting de EPAM.  
> Los logs JSON usan el mismo formato que el `loggen.sh` del **lab-09-cloudwatch-logs**,
> y las métricas que reporta son equivalentes a las queries de **CloudWatch Logs Insights**
> y a las de **Prometheus** del lab-07.

---

## Flujo

```
[lab-09] EC2 + loggen.sh ──► CloudWatch Log Group /epam/lab/app
                 │
                 ▼  (mismo formato JSON)
         generate_logs.py   ◄── genera app.log local para practicar
                 │
                 ▼
         log_analyzer.py    ◄── Ejercicio 1: parseo, métricas, SLO check
                 │
                 ▼
         s3_janitor.py      ◄── Ejercicio 2: boto3 + moto (próximamente)
```

---

## Setup

```bash
# Desde la raíz del repo
python3 -m venv .venv
source .venv/bin/activate
pip install boto3 moto pytest

cd labs/scripting
```

---

## Ejercicio 1 — Log Analyzer

### Paso 1: Genera el log

```bash
python generate_logs.py              # 500 líneas -> app.log
python generate_logs.py --lines 2000 # más datos
python generate_logs.py --out /tmp/app.log
```

### Paso 2: Analiza

```bash
python log_analyzer.py               # SLO default 99.5%
python log_analyzer.py --slo 99.9    # SLO estricto de producción
python log_analyzer.py --log /tmp/app.log --slo 99.9
```

### Output esperado

```
==========================================================
  [LOG ANALYZER] — EPAM Scripting Exercise (streaming)
==========================================================
  Total requests : 2,000
  INFO / WARN / ERROR : 1,700 / 160 / 140

  [*]  Status code breakdown:
     200  ######################       1700
     400  ###                160
     500  ##                  140

  [t]  Latencia (reservoir sampling):
     avg=312ms  p50=290ms  p95=1820ms  p99=2380ms

  [!]  Top endpoints con errores 5xx:
     38x  POST /api/v1/payments
     ...

  [OK]  SLO 99.5% availability: CUMPLIDO
==========================================================
```

---

## Equivalencias con otros labs

| Métrica de log_analyzer.py | CloudWatch Logs Insights (lab-09) | PromQL (lab-07) |
|---|---|---|
| Error rate 5xx | `filter status >= 500 \| stats count()` | `rate(http_requests_total{status=~"5.."}[5m])` |
| p95 latencia | `stats pct(latency_ms, 95) by endpoint` | `histogram_quantile(0.95, rate(http_duration_bucket[5m]))` |
| Top errores | `stats count() by error \| sort desc` | `topk(5, rate(errors_total[5m]))` |

---

## Ejercicios bonus con jq (bash)

```bash
# Top endpoints por requests
jq -r '.endpoint' app.log | sort | uniq -c | sort -nr | head

# Errores por tipo
jq -r 'select(.error != "") | .error' app.log | sort | uniq -c | sort -nr

# P95 de latencia sin numpy
jq -r '.latency_ms' app.log | sort -n | awk 'BEGIN{c=0} {lines[c++]=$0} END{print lines[int(c*0.95)]}'

# Requests de un usuario específico
jq 'select(.user == "alice")' app.log | jq -s 'length'

# Correlación: buscar request_id en el log
jq 'select(.request_id == "<uuid-aqui>")' app.log
```

---

## Archivos

| Archivo | Descripción |
|---|---|
| `generate_logs.py` | Genera `app.log` JSON — mismo formato que `loggen.sh` de lab-09 |
| `log_analyzer.py` | Ejercicio 1: análisis completo con SLO check (streaming) |
| `python-codility-fundamentals.py` | Fundamentos de Python para Codility (sintaxis, estructuras, patrones) |
| `codility-exam-2026-05-06.py` | **Examen Codility real — Score 100%** (2 tasks) |
| `s3_janitor.py` | Ejercicio 2: boto3 + moto (próximamente) |
| `app.log` | Generado localmente — en `.gitignore` |

---

## Codility Assessment — 2026-05-06

> **Score: 100%** — 2/2 tasks con puntuación perfecta.
> Invitación recibida de EPAM Systems Inc. (ivan_kokosh@epam.com) el 4 de mayo.
> Deadline original: Mayo 7, 09:00 UTC. Completado: Mayo 6, 14:20 CST.

### Timeline

| Fecha | Evento |
|---|---|
| 2026-05-04 | Invitación recibida de EPAM via Codility |
| 2026-05-05 | Reminder recibido |
| 2026-05-06 14:10 | Inicio del examen |
| 2026-05-06 14:14 | Task 1 submitted (largest_letter) — 100% |
| 2026-05-06 14:20 | Task 2 submitted (generate_palindrome) — 100% |

### Task 1: `largest_letter` — 100%

**Problema:** Dado un string S, encontrar la letra alfabéticamente más grande que aparezca tanto en minúscula como en mayúscula. Si no existe, retornar `"NO"`.

- Correctness: 100% (6/6 tests)
- Performance: 100% (4/4 tests)
- **Técnica clave:** Sets + intersección para O(n)

### Task 2: `generate_palindrome` — 100%

**Problema:** Dados N y K, generar un palíndromo de longitud N con exactamente K letras minúsculas distintas.

- Correctness: 100% (8/8 tests)
- **Técnica clave:** Construir primera mitad ciclando K letras, espejar para crear palíndromo

### Soluciones

Ver archivo: [`codility-exam-2026-05-06.py`](codility-exam-2026-05-06.py)

---

## 🎯 Scripting Interview Prep — EPAM DevOps Cloud Engineer

> Mock exercises, code review y cheat sheet para la prueba de scripting.  
> Usa `generate_logs.py` para generar datos de práctica.

---

## 1. Mini Mock — Ejercicios tipo EPAM

**Reglas:**
- No mires tu `log_analyzer.py` ni apuntes.
- Cronométrate: máximo 15 min por ejercicio.
- Piensa en voz alta como si estuvieras en la entrevista.

---

### Mock 1 — Log Error Report (Python)

**Prompt del entrevistador:**
> "Tengo un archivo `app.log` con líneas JSON. Cada línea tiene los campos: `timestamp`, `level`, `status`, `endpoint`, `latency_ms`, `user`, `request_id`, `error`.
> Escríbeme un script en Python que:
> 1. Lea el archivo.
> 2. Muestre el total de requests.
> 3. Muestre el error rate (status >= 500).
> 4. Muestre el top 5 de endpoints con más errores 5xx.
> 5. Me diga si cumple un SLO de 99.5% de disponibilidad."

<details>
<summary>💡 Solución de referencia</summary>

```python
#!/usr/bin/env python3
"""Mini mock 1 — Log Error Report."""
import json
from collections import Counter

LOG = "app.log"
SLO = 99.5

records = []
with open(LOG) as f:
    for line in f:
        records.append(json.loads(line))

total = len(records)
errors_5xx = [r for r in records if r["status"] >= 500]
error_count = len(errors_5xx)
error_rate = error_count / total * 100
availability = 100 - error_rate

endpoint_errors = Counter(r["endpoint"] for r in errors_5xx)
top5 = endpoint_errors.most_common(5)

print(f"Total requests : {total}")
print(f"5xx errors     : {error_count}")
print(f"Error rate     : {error_rate:.2f}%")
print(f"Availability   : {availability:.2f}%")
print()
print("Top 5 endpoints con errores 5xx:")
for ep, count in top5:
    print(f"  {count:>4}x  {ep}")
print()
slo_ok = availability >= SLO
print(f"SLO {SLO}%: {'CUMPLIDO' if slo_ok else 'INCUMPLIDO'}")
```

</details>

---

### Mock 2 — S3 Bucket Cleanup (Python + boto3)

**Prompt del entrevistador:**
> "Escríbeme un script en Python con boto3 que:
> 1. Liste todos los buckets de S3.
> 2. Para cada bucket, cuente cuántos objetos tiene.
> 3. Identifique buckets vacíos (0 objetos).
> 4. Imprima un reporte con: nombre del bucket, cantidad de objetos, y si está vacío.
> 5. Bonus: que acepte un flag `--delete` para borrar los buckets vacíos."

<details>
<summary>💡 Solución de referencia</summary>

```python
#!/usr/bin/env python3
"""Mini mock 2 — S3 Bucket Cleanup."""
import argparse
import boto3

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--delete", action="store_true", help="Delete empty buckets")
    args = parser.parse_args()

    s3 = boto3.client("s3")
    buckets = s3.list_buckets()["Buckets"]

    empty = []
    print(f"{'Bucket':<40} {'Objects':>8}  Status")
    print("-" * 60)

    for b in buckets:
        name = b["Name"]
        resp = s3.list_objects_v2(Bucket=name, MaxKeys=1)
        count = resp.get("KeyCount", 0)
        status = "EMPTY" if count == 0 else "has objects"
        print(f"{name:<40} {count:>8}  {status}")
        if count == 0:
            empty.append(name)

    print(f"\nEmpty buckets: {len(empty)}")

    if args.delete and empty:
        for name in empty:
            print(f"  Deleting {name}...")
            s3.delete_bucket(Bucket=name)
            print(f"  Deleted {name}")

if __name__ == "__main__":
    main()
```

</details>

---

### Mock 3 — Bash One-Liners

**Prompt del entrevistador:**
> "Resuelve cada uno con un one-liner de bash."
> 1. Top 5 endpoints por cantidad de requests en `app.log`
> 2. Error rate (5xx) como porcentaje
> 3. P95 de latencia
> 4. Top 10 procesos por uso de memoria en el sistema
> 5. Cantidad de conexiones TCP establecidas agrupadas por IP remota

<details>
<summary>💡 Soluciones de referencia</summary>

```bash
# 1. Top 5 endpoints
jq -r '.endpoint' app.log | sort | uniq -c | sort -nr | head -5

# 2. Error rate
echo "scale=2; $(jq 'select(.status>=500)' app.log | jq -s 'length') * 100 / $(wc -l < app.log)" | bc

# 3. P95 de latencia
jq -r '.latency_ms' app.log | sort -n | awk '{a[NR]=$0} END{print a[int(NR*0.95)]}'

# 4. Top 10 procesos por memoria
ps aux --sort=-%mem | head -11

# 5. Conexiones TCP por IP remota
ss -tn state established | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -nr | head
```

</details>

---

### Mock 4 — Kubernetes Log Troubleshooting (Bash)

**Prompt del entrevistador:**
> "Un pod llamado `payments-api` en el namespace `production` está en `CrashLoopBackOff`. Dame los comandos que usarías para diagnosticarlo, en orden."

<details>
<summary>💡 Solución de referencia</summary>

```bash
# 1. Ver estado actual del pod
kubectl get pod payments-api -n production -o wide

# 2. Ver eventos y razón del crash
kubectl describe pod payments-api -n production

# 3. Ver logs del contenedor actual (o último crash)
kubectl logs payments-api -n production
kubectl logs payments-api -n production --previous

# 4. Ver si tiene resource limits que causen OOMKilled
kubectl get pod payments-api -n production -o jsonpath='{.status.containerStatuses[*].lastState}'

# 5. Ver recursos del nodo
kubectl top node
kubectl describe node <node-name> | grep -A10 "Allocated resources"

# 6. Si necesitas entrar al pod (si arranca brevemente)
kubectl exec -it payments-api -n production -- sh
```

</details>

---

### Mock 5 — Script de Health Check (Python)

**Prompt del entrevistador:**
> "Escríbeme un script que haga health check a una lista de URLs. Para cada URL:
> - Haz un GET request
> - Si responde 200 en menos de 2 segundos → HEALTHY
> - Si responde otro status o tarda más de 2s → UNHEALTHY
> - Si no responde → DOWN
>
> Imprime un reporte al final."

<details>
<summary>💡 Solución de referencia</summary>

```python
#!/usr/bin/env python3
"""Mini mock 5 — Health Checker."""
import requests

URLS = [
    "https://httpbin.org/status/200",
    "https://httpbin.org/status/500",
    "https://httpbin.org/delay/5",
    "https://esto-no-existe.invalid",
]
TIMEOUT = 2

results = []
for url in URLS:
    try:
        r = requests.get(url, timeout=TIMEOUT)
        if r.status_code == 200:
            status = "HEALTHY"
        else:
            status = f"UNHEALTHY ({r.status_code})"
    except requests.exceptions.Timeout:
        status = "UNHEALTHY (timeout)"
    except requests.exceptions.ConnectionError:
        status = "DOWN"
    results.append((url, status))

print(f"\n{'URL':<45} Status")
print("-" * 65)
for url, status in results:
    print(f"{url:<45} {status}")
```

</details>

---

### Mock 6 — Version Sort & Artifact Management (Bash + Python)

**Prompt del entrevistador:**
> "Tenemos artefactos deployados en S3 con nombres como `my-app-1.2.3.tar.gz`.
> Necesito que:
> 1. De una lista de versiones, me digas cuál es la más reciente y la más antigua.
> 2. Ordénalas de menor a mayor.
> 3. Bonus: hazlo en bash Y en python."

**Contexto:**
> `sort` normal falla con versiones porque compara caracteres, no números:
> `"1.10.1"` aparece antes que `"1.9.4"` porque `'1' < '9'` carácter a carácter.
> Necesitas `sort -V` (version sort) o lógica equivalente.

<details>
<summary>💡 Solución de referencia — Bash</summary>

```bash
VERSIONS="1.2.3
1.10.1
1.9.4
2.0.0
0.9.1
1.2.14
1.2.3-rc1"

# Ordenar de menor a mayor
echo "$VERSIONS" | sort -V

# Version más reciente
echo "$VERSIONS" | sort -V | tail -1   # → 2.0.0

# Version más antigua
echo "$VERSIONS" | sort -V | head -1   # → 0.9.1

# Desde git tags
git tag | sort -V | tail -1

# Desde artefactos en S3
aws s3 ls s3://artifacts/my-app/ \
  | awk '{print $4}' \
  | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' \
  | sort -V | tail -1

# Top 5 versiones más recientes
echo "$VERSIONS" | sort -Vr | head -5

# Fallback si sort -V no existe (Alpine mínimo, macOS viejo)
echo "$VERSIONS" | awk -F. '{printf "%04d%04d%04d %s\n", $1, $2, $3, $0}' \
  | sort -n | awk '{print $2}'
```

**Tabla de referencia rápida:**
```
Comando    Qué hace                          Entiende versiones?
sort       orden alfabético ("10" < "2")     NO
sort -n    orden numérico (no entiende .)    NO
sort -V    orden de versiones (1.9 < 1.10)   SI
sort -Vr   versiones en reverso              SI
```

</details>

<details>
<summary>💡 Solución de referencia — Python</summary>

```python
#!/usr/bin/env python3
"""Mini mock 6 — Version Sorter."""

versions = ["1.2.3", "1.10.1", "1.9.4", "2.0.0", "0.9.1", "1.2.14"]

# Convertir "1.10.1" → (1, 10, 1) como tupla de ints
# Python compara tuplas elemento por elemento → orden correcto
sorted_versions = sorted(versions, key=lambda v: tuple(map(int, v.split("."))))

print("Ordenadas:")
for v in sorted_versions:
    print(f"  {v}")

print(f"\nMas antigua : {sorted_versions[0]}")
print(f"Mas reciente: {sorted_versions[-1]}")
```

```python
# Version con pre-release (bonus avanzado)
from packaging.version import Version   # pip install packaging

versions = ["1.2.3", "1.2.3rc1", "1.2.3a1", "1.2.4", "2.0.0"]
sorted_v = sorted(versions, key=Version)
# ['1.2.3a1', '1.2.3rc1', '1.2.3', '1.2.4', '2.0.0']
```

```python
# Comparar dos versiones específicas
def version_gt(v1, v2):
    t1 = tuple(map(int, v1.split(".")))
    t2 = tuple(map(int, v2.split(".")))
    return t1 > t2

print(version_gt("1.10.1", "1.9.4"))   # True
print(version_gt("1.2.3", "1.2.14"))   # False
```

</details>

---

### Mock 7 — Streaming Log Processor (Python)

**Prompt del entrevistador:**
> "El archivo `app.log` en producción puede pesar 50 GB. El script del Mock 1 carga todo
> en memoria y muere con OOMKilled.
> Reescríbelo para que:
> 1. Procese el archivo línea por línea (streaming) usando memoria constante.
> 2. También funcione leyendo desde `stdin` (pipe).
> 3. Maneje líneas JSON corruptas sin crashear.
> 4. Imprima el mismo reporte que Mock 1."

**Contexto:**
> `for line in f` es un **iterador** — Python lee un buffer del disco (~8 KB) y te entrega
> una línea a la vez. La línea anterior se descarta de memoria.
>
> `[json.loads(l) for l in f]` carga **todo** en una lista en RAM → explota.

<details>
<summary>💡 Solución de referencia</summary>

```python
#!/usr/bin/env python3
"""Mini mock 7 — Streaming Log Processor.
Memoria constante sin importar el tamaño del archivo.
Soporta archivo o stdin: cat app.log | python mock7.py
"""
import sys
import json
import argparse
from collections import Counter

def parse_args():
    parser = argparse.ArgumentParser(description="Streaming log analyzer")
    parser.add_argument("--log", default=None, help="Log file (default: stdin)")
    parser.add_argument("--slo", type=float, default=99.5)
    return parser.parse_args()

def analyze_stream(source):
    """Procesa linea por linea — memoria O(1) excepto los contadores."""
    total = 0
    errors_5xx = 0
    endpoint_errors = Counter()
    corrupted = 0

    for line in source:                          # UNA linea a la vez
        try:
            record = json.loads(line)
        except json.JSONDecodeError:
            corrupted += 1
            continue                             # no crashear por 1 linea mala
        total += 1
        if record.get("status", 0) >= 500:
            errors_5xx += 1
            endpoint_errors[record.get("endpoint", "unknown")] += 1
        # `record` y `line` se descartan aqui → garbage collector libera RAM

    return {"total": total, "errors_5xx": errors_5xx,
            "endpoint_errors": endpoint_errors, "corrupted": corrupted}

def report(stats, slo):
    total = stats["total"]
    if total == 0:
        print("No records found.")
        return False
    error_rate = stats["errors_5xx"] / total * 100
    availability = 100 - error_rate
    top5 = stats["endpoint_errors"].most_common(5)

    print(f"Total requests : {total:,}")
    print(f"5xx errors     : {stats['errors_5xx']:,}")
    print(f"Error rate     : {error_rate:.2f}%")
    print(f"Availability   : {availability:.2f}%")
    if stats["corrupted"]:
        print(f"Skipped {stats['corrupted']} corrupted lines")
    print()
    print("Top 5 endpoints con errores 5xx:")
    for ep, count in top5:
        print(f"  {count:>4}x  {ep}")
    print()
    slo_ok = availability >= slo
    print(f"SLO {slo}%: {'CUMPLIDO' if slo_ok else 'INCUMPLIDO'}")
    return slo_ok

def main():
    args = parse_args()
    if args.log:
        try:
            source = open(args.log)
        except FileNotFoundError:
            print(f"Error: {args.log} not found", file=sys.stderr)
            sys.exit(1)
    else:
        source = sys.stdin

    with source:
        stats = analyze_stream(source)
        slo_ok = report(stats, args.slo)
    sys.exit(0 if slo_ok else 1)

if __name__ == "__main__":
    main()
```

```bash
# Ambas formas funcionan:
python mock7.py --log app.log --slo 99.9
cat app.log | python mock7.py --slo 99.9
tail -f /var/log/app.log | python mock7.py
```

**Comparacion de memoria:**
```
                    Mock 1 (lista)    Mock 7 (streaming)
app.log 1 MB        ~5 MB RAM         ~10 KB RAM
app.log 1 GB        ~5 GB RAM         ~10 KB RAM
app.log 50 GB       OOMKilled         ~10 KB RAM  OK
stdin infinito      imposible         corre indefinidamente
```

</details>

---

### Mock 8 — Disk & Process Triage (Bash)

**Prompt del entrevistador:**
> "Un servidor Linux se quedó sin espacio en disco. Dame los one-liners para:
> 1. Ver el uso de disco por filesystem.
> 2. Encontrar los 10 archivos más grandes en `/var/log`.
> 3. Encontrar directorios que usen más de 1 GB.
> 4. Ver qué procesos tienen archivos abiertos que ya se borraron (deleted).
> 5. Rotar/vaciar un log sin matar el proceso que escribe."

<details>
<summary>💡 Soluciones de referencia</summary>

```bash
# 1. Uso de disco por filesystem
df -h

# 2. Top 10 archivos más grandes en /var/log
find /var/log -type f -exec du -h {} + 2>/dev/null | sort -rh | head -10

# 3. Directorios que usan más de 1 GB
du -h --max-depth=2 / 2>/dev/null | awk '$1 ~ /G/ && $1+0 > 1'

# 4. Procesos con archivos borrados (espacio "fantasma")
lsof +L1 2>/dev/null | grep deleted

# 5. Vaciar log SIN matar el proceso (truncate)
truncate -s 0 /var/log/app.log
# o
> /var/log/app.log
```

**Concepto clave para la entrevista:**
```
rm archivo.log  →  borra el nombre del archivo (el inode sigue ocupado
                   mientras algún proceso tenga el fd abierto)
                →  df sigue mostrando disco lleno

truncate -s 0   →  vacía el contenido pero mantiene el file descriptor
                →  el proceso sigue escribiendo sin errores
                →  el espacio se libera inmediatamente
```

</details>

---

### Mock 9 — AWS Resource Audit (Bash One-Liners)

**Prompt del entrevistador:**
> "Usando AWS CLI, dame one-liners para:
> 1. Listar todas las EC2 corriendo con su nombre, IP privada y tipo de instancia.
> 2. Encontrar Security Groups que permiten 0.0.0.0/0 en el puerto 22 (SSH abierto al mundo).
> 3. Listar roles IAM que no se han usado en más de 90 días.
> 4. Encontrar EBS volumes no attached (desperdicio de dinero).
> 5. Listar S3 buckets sin encryption habilitado."

<details>
<summary>💡 Soluciones de referencia</summary>

```bash
# 1. EC2 corriendo: nombre, IP, tipo
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value|[0],PrivateIpAddress,InstanceType]' \
  --output table

# 2. Security Groups con SSH abierto al mundo
aws ec2 describe-security-groups \
  --query 'SecurityGroups[?IpPermissions[?FromPort==`22` && IpRanges[?CidrIp==`0.0.0.0/0`]]].[GroupId,GroupName]' \
  --output table

# 3. Roles IAM no usados en 90+ días
aws iam list-roles --query 'Roles[].[RoleName,RoleLastUsed.LastUsedDate]' --output table

# 4. EBS volumes sin usar
aws ec2 describe-volumes \
  --filters "Name=status,Values=available" \
  --query 'Volumes[].[VolumeId,Size,CreateTime]' \
  --output table

# 5. S3 buckets sin encryption
for bucket in $(aws s3api list-buckets --query 'Buckets[].Name' --output text); do
  enc=$(aws s3api get-bucket-encryption --bucket "$bucket" 2>&1)
  if echo "$enc" | grep -q "ServerSideEncryptionConfigurationNotFoundError"; then
    echo "NO ENCRYPTION: $bucket"
  fi
done
```

</details>

---

### Mock 10 — Config File Parser & Validator (Python)

**Prompt del entrevistador:**
> "Escríbeme un script que valide archivos YAML de Kubernetes.
> Dado un directorio con manifests `.yaml`:
> 1. Parsea cada archivo.
> 2. Verifica que todo Deployment tenga `resources.requests` y `resources.limits`.
> 3. Verifica que no haya containers corriendo como `root` (`securityContext.runAsNonRoot`).
> 4. Imprime un reporte de violaciones.
> 5. Exit code 1 si hay violaciones (para usar en CI)."

<details>
<summary>💡 Solución de referencia</summary>

```python
#!/usr/bin/env python3
"""Mini mock 10 — K8s Manifest Validator."""
import sys
import yaml
from pathlib import Path

def check_deployment(manifest, filename):
    violations = []
    if manifest.get("kind") != "Deployment":
        return violations

    name = manifest.get("metadata", {}).get("name", "unknown")
    containers = (manifest.get("spec", {})
                  .get("template", {})
                  .get("spec", {})
                  .get("containers", []))

    for c in containers:
        cname = c.get("name", "unnamed")
        prefix = f"{filename} -> {name}/{cname}"

        resources = c.get("resources", {})
        if not resources.get("requests"):
            violations.append(f"  WARN  {prefix}: missing resources.requests")
        if not resources.get("limits"):
            violations.append(f"  WARN  {prefix}: missing resources.limits")

        sc = c.get("securityContext", {})
        pod_sc = (manifest.get("spec", {})
                  .get("template", {})
                  .get("spec", {})
                  .get("securityContext", {}))
        if not sc.get("runAsNonRoot") and not pod_sc.get("runAsNonRoot"):
            violations.append(f"  FAIL  {prefix}: runAsNonRoot not set")

    return violations

def main():
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    yamls = list(target.glob("**/*.yaml")) + list(target.glob("**/*.yml"))

    if not yamls:
        print(f"No YAML files found in {target}")
        sys.exit(0)

    all_violations = []
    for yf in sorted(yamls):
        try:
            docs = yaml.safe_load_all(yf.read_text())
            for doc in docs:
                if doc:
                    all_violations.extend(check_deployment(doc, yf.name))
        except yaml.YAMLError as e:
            all_violations.append(f"  ERROR {yf.name}: invalid YAML — {e}")

    print(f"\nScanned {len(yamls)} files")
    if all_violations:
        print(f"Found {len(all_violations)} violations:\n")
        for v in all_violations:
            print(v)
        sys.exit(1)
    else:
        print("All checks passed")
        sys.exit(0)

if __name__ == "__main__":
    main()
```

```bash
# Uso:
python mock10.py ./k8s-manifests/
python mock10.py ./labs/lab-04-eks-cluster/k8s/

# En CI (GitLab):
# validate:
#   script:
#     - pip install pyyaml
#     - python mock10.py ./k8s/
```

</details>

---

## 2. Code Review — `log_analyzer.py`

### Buenas prácticas que deberías tener

- [ ] Usa `argparse` para `--log`, `--slo`, etc.
- [ ] Maneja `FileNotFoundError` al abrir el archivo
- [ ] Maneja `json.JSONDecodeError` por líneas corruptas
- [ ] Usa `Counter` o `defaultdict` en vez de dicts manuales
- [ ] Calcula percentiles correctamente (`sorted` + index)
- [ ] Separa lógica en funciones (`parse`, `analyze`, `report`)
- [ ] Tiene `if __name__ == "__main__"`
- [ ] Tiene docstrings o comentarios claros
- [ ] El output es legible y formateado
- [ ] Exit code `!= 0` si el SLO no se cumple

### Red flags que evitar

- [ ] No hardcodees rutas absolutas
- [ ] No uses bare `except` — usa `except Exception as e`
- [ ] No leas todo el archivo en memoria si puede ser enorme → procesa línea por línea (ver Mock 7)
- [ ] No imprimas stack traces al usuario final → atrapa excepciones y muestra mensaje limpio
- [ ] No mezcles lógica de negocio con `print()` → separa análisis de presentación

### Cosas que impresionan al entrevistador

- Que el script retorne `exit code 1` si SLO falla → útil en pipelines CI/CD
- Que soporte `stdin` además de archivo → `cat app.log | python log_analyzer.py` (ver Mock 7)
- Que tenga `--format json` para output máquina
- Que uses `sort -V` y no `sort` para versiones (ver Mock 6)
- Que sepas la diferencia entre `rm` y `truncate` para logs (ver Mock 8)
- Que menciones: *"en producción usaría CloudWatch Logs Insights o PromQL, pero este script es útil para debugging local"*

---

## 3. Cheat Sheet — Python + Bash para Entrevista

### Python esencial

```python
# Leer archivo JSON línea por línea (STREAMING — memoria constante)
import json
with open("app.log") as f:
    for line in f:                     # iterador — una línea a la vez
        record = json.loads(line)
        # procesar y acumular solo lo necesario

# Leer todo en memoria (SOLO si cabe)
with open("app.log") as f:
    records = [json.loads(line) for line in f]

# Soportar archivo O stdin
import sys
source = open(args.log) if args.log else sys.stdin
with source:
    for line in source:
        ...

# Contar ocurrencias
from collections import Counter
counts = Counter(r["status"] for r in records)
# counts.most_common(5) → [(200, 1700), (500, 140), ...]

# Agrupar por campo
from collections import defaultdict
by_endpoint = defaultdict(list)
for r in records:
    by_endpoint[r["endpoint"]].append(r)

# Filtrar
errors = [r for r in records if r["status"] >= 500]

# Percentil sin numpy
def percentile(data, p):
    s = sorted(data)
    i = int(len(s) * p / 100)
    return s[min(i, len(s) - 1)]

# Ordenar versiones semánticas
versions = ["1.2.3", "1.10.1", "1.9.4", "2.0.0"]
sorted(versions, key=lambda v: tuple(map(int, v.split("."))))
# → ['1.2.3', '1.9.4', '1.10.1', '2.0.0']

# Comparar dos versiones
def version_gt(v1, v2):
    return tuple(map(int, v1.split("."))) > tuple(map(int, v2.split(".")))

# Formateo
print(f"{'Name':<30} {'Count':>8}")
print(f"{name:<30} {count:>8,}")

# argparse básico
import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--log", default="app.log")
parser.add_argument("--slo", type=float, default=99.5)
args = parser.parse_args()

# boto3 S3 básico
import boto3
s3 = boto3.client("s3")
buckets = s3.list_buckets()["Buckets"]
objects = s3.list_objects_v2(Bucket="name", MaxKeys=100)

# Manejo de errores
try:
    with open(args.log) as f:
        for line in f:
            try:
                record = json.loads(line)
            except json.JSONDecodeError:
                continue                  # skip línea corrupta
except FileNotFoundError:
    print(f"Error: {args.log} not found", file=sys.stderr)
    sys.exit(1)

# sys.exit con código
import sys
sys.exit(0 if slo_ok else 1)
```

### Bash esencial

```bash
# jq básico
jq '.status' app.log                           # extraer campo
jq 'select(.status >= 500)' app.log            # filtrar
jq -r '.endpoint' app.log                      # raw output (sin comillas)
jq -s 'length' app.log                         # contar líneas (slurp)
jq -s 'map(.latency_ms) | sort | .[-1]' app.log  # max latency

# Contar y ordenar
sort | uniq -c | sort -nr | head -5

# Ordenar versiones
sort -V                                        # version sort (1.9 < 1.10)
sort -Vr                                       # version sort reverso
echo "$VERSIONS" | sort -V | tail -1           # versión más reciente
git tag | sort -V | tail -1                    # último tag del repo

# Fallback si sort -V no existe
echo "$VERSIONS" | awk -F. '{printf "%04d%04d%04d %s\n",$1,$2,$3,$0}' | sort -n | awk '{print $2}'

# awk
awk '{print $1}'                               # primer campo
awk -F: '{print $1}'                           # delimitador custom
awk '{sum+=$1} END{print sum/NR}'              # promedio
awk '{a[NR]=$0} END{print a[int(NR*0.95)]}'   # p95

# grep
grep -c "ERROR" app.log                        # contar matches
grep -B2 -A5 "ERROR" app.log                   # contexto
grep -E "status\":\s*5[0-9]{2}" app.log        # regex

# Disco
df -h                                          # uso por filesystem
du -h --max-depth=2 / 2>/dev/null | sort -rh | head
find /var/log -type f -exec du -h {} + | sort -rh | head -10
lsof +L1 | grep deleted                        # archivos borrados aún abiertos
truncate -s 0 /var/log/app.log                 # vaciar sin matar proceso
# rm NO libera espacio si el proceso tiene el fd abierto

# Procesos y red
ps aux --sort=-%mem | head -11                 # top 10 por mem
ps aux --sort=-%cpu | head -11                 # top 10 por cpu
ss -tlnp | grep 8080                           # quién usa puerto
ss -tn state established | wc -l              # conexiones activas
lsof -i :8080                                  # proceso en puerto

# AWS CLI
aws s3 ls                                      # listar buckets
aws s3 ls s3://bucket --recursive --summarize  # contar objetos
aws logs filter-log-events \
  --log-group-name /epam/lab/app \
  --filter-pattern "ERROR"                     # buscar en CW Logs

# AWS Auditoría (Mock 9)
aws ec2 describe-instances \
  --filters "Name=instance-state-name,Values=running" \
  --query 'Reservations[].Instances[].[Tags[?Key==`Name`].Value|[0],PrivateIpAddress,InstanceType]' \
  --output table

aws ec2 describe-volumes --filters "Name=status,Values=available" \
  --query 'Volumes[].[VolumeId,Size,CreateTime]' --output table

# Loop con AWS CLI
for bucket in $(aws s3 ls | awk '{print $3}'); do
  count=$(aws s3 ls "s3://$bucket" --recursive | wc -l)
  echo "$bucket: $count objects"
done

# Kubernetes
kubectl get pods -A -o wide                    # todos los pods
kubectl top pods -n production                 # consumo recursos
kubectl logs deploy/app -n production -f       # logs en vivo
kubectl rollout undo deploy/app                # rollback
kubectl exec -it pod-name -- sh                # shell en pod
```

### Frases útiles durante la entrevista

```
Antes de escribir:
  "Let me think about the approach first."
  "I'll start simple and iterate."

Si te trabas:
  "I know the concept — let me look up the exact syntax."
  "In production I'd use [X tool], but for this exercise..."

Si no sabes:
  "I haven't used that specific tool, but I've solved
   similar problems with [alternativa]."

Al terminar:
  "For production I'd add error handling and logging."
  "This could also be done with a CloudWatch Logs Insights query."
  "I'd add unit tests with pytest and moto for the AWS calls."
  "I'd process this as a stream for large files instead of loading all into memory."
```

---

## 4. Conceptos Clave — Quick Reference

### Streaming vs Load All

```
for line in f:              →  stream (O(1) memoria, archivos infinitos)  OK
[json.loads(l) for l in f]  →  carga todo (O(n) memoria, explota)        CUIDADO
f.read()                    →  un string gigante en RAM                   PELIGRO
```

### sort normal vs sort -V

```
sort      →  "1.10" < "1.9"   (compara caracteres)     MAL
sort -V   →  "1.10" > "1.9"   (compara versiones)      BIEN
```

### rm vs truncate

```
rm app.log       →  borra nombre, fd sigue abierto, disco NO se libera
truncate -s 0    →  vacía contenido, fd válido, disco se libera
```

### Exit codes en scripts

```
exit 0  →  éxito     (SLO cumplido, validación pasó)
exit 1  →  fallo     (SLO incumplido, violaciones encontradas)
# Útil en CI/CD: el pipeline falla automáticamente si exit != 0
```

---

## 5. Rutina pre-entrevista

1. [ ] Genera logs: `python generate_logs.py --lines 1000`
2. [ ] Haz Mock 1 desde cero sin mirar código (15 min máx)
3. [ ] Haz los 5 one-liners de Mock 3
4. [ ] Haz Mock 6: ordena versiones en bash y python (5 min)
5. [ ] Haz Mock 7: reescribe Mock 1 en modo streaming (10 min)
6. [ ] Haz Mock 8: one-liners de disco (5 min)
7. [ ] Revisa tu `log_analyzer.py` con el checklist de §2
8. [ ] Repasa el cheat sheet de §3 y conceptos clave de §4
9. [ ] Practica en voz alta en inglés mientras codificas
10. [ ] Duerme bien — eso importa más que una hora extra de estudio

---

## 📖 Documentación Relacionada

- **[docs/05-observability-concepts.md](../../docs/05-observability-concepts.md)** — Conceptos de observabilidad
- **[docs/06-scripting-coding-prep.md](../../docs/06-scripting-coding-prep.md)** — Preparación de scripting
- [Lab 07 — Prometheus + Grafana](../lab-07-monitoring/Readme.md) — Métricas en EKS
- [Lab 09 — CloudWatch Logs](../lab-09-cloudwatch-logs/Readme.md) — Logs en EC2/AWS
- [warmup_exercises.md](./warmup_exercises.md) — 3 ejercicios de calentamiento (20 min)
- [bonus_practice.md](./bonus_practice.md) — 12 ejercicios adicionales
