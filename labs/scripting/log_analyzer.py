#!/usr/bin/env python3
"""
log_analyzer.py  —  Ejercicio 1 de scripting EPAM

Lee app.log (JSON estructurado) en modo STREAMING — una linea a la vez,
sin cargar el archivo completo en memoria. Apto para archivos de cualquier
tamano (GB, TB).

Reporta:
  - Conteo por level / status code
  - Top 5 endpoints con mas errores 5xx
  - Percentiles de latencia (p50, p95, p99) via reservoir sampling
  - Error rate y SLO check
  - Top errores por tipo

Relacion con labs:
  lab-07: equivalente Python de la query PromQL de error rate
  lab-09: analiza los mismos logs que CloudWatch Logs Insights procesa

CloudWatch Logs Insights equivalente:
    fields endpoint, status, latency_ms
    | filter status >= 500
    | stats count() as errors, pct(latency_ms, 95) as p95 by endpoint
    | sort errors desc

Uso:
    python log_analyzer.py                    # analiza app.log
    python log_analyzer.py --log /ruta/app.log
    python log_analyzer.py --slo 99.9
    python log_analyzer.py --sample 50000     # tamano del reservoir (default: 10000)
"""

import json
import argparse
import random
import sys
from collections import defaultdict


# ---------------------------------------------------------------------------
# Generador — lee UNA linea a la vez, nunca carga el archivo completo
# ---------------------------------------------------------------------------
def stream_log(log_path: str):
    """
    Generador que hace yield de cada registro JSON de a uno.
    RAM usada: solo el registro actual, no el archivo completo.
    """
    parse_errors = 0
    with open(log_path, "r") as f:
        for lineno, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                yield json.loads(line)
            except json.JSONDecodeError:
                parse_errors += 1
                if parse_errors <= 5:  # no spamear en archivos grandes
                    print(f"  [WARN]  Linea {lineno} no es JSON valido, se omite.")
    if parse_errors > 5:
        print(f"  [WARN]  {parse_errors} lineas invalidas en total omitidas.")


# ---------------------------------------------------------------------------
# Reservoir sampling — percentiles aproximados sin guardar todos los valores
#
# Algoritmo: para cada elemento i, lo agrega al reservoir con probabilidad
# SAMPLE_SIZE/i. Resultado: muestra aleatoria uniforme de cualquier stream.
# Con 10k muestras el error en p95/p99 es < 1%.
# ---------------------------------------------------------------------------
class ReservoirSampler:
    def __init__(self, size: int):
        self.size = size
        self.reservoir = []
        self.count = 0

    def add(self, value: float):
        self.count += 1
        if len(self.reservoir) < self.size:
            self.reservoir.append(value)
        else:
            j = random.randint(0, self.count - 1)
            if j < self.size:
                self.reservoir[j] = value

    def percentile(self, p: int) -> float:
        if not self.reservoir:
            return 0.0
        s = sorted(self.reservoir)
        idx = max(0, int(len(s) * p / 100) - 1)
        return s[idx]

    def avg(self) -> float:
        return sum(self.reservoir) / len(self.reservoir) if self.reservoir else 0.0


# ---------------------------------------------------------------------------
# Analisis en streaming — O(1) memoria respecto al tamano del archivo
# ---------------------------------------------------------------------------
def analyze_stream(log_path: str, slo_target: float, sample_size: int):
    level_counts  = defaultdict(int)
    status_counts = defaultdict(int)
    endpoint_5xx  = defaultdict(int)
    error_types   = defaultdict(int)
    total         = 0

    # Reservoir samplers — usan memoria fija independiente del archivo
    sampler_all = ReservoirSampler(sample_size)
    sampler_5xx = ReservoirSampler(sample_size)

    for r in stream_log(log_path):
        total += 1
        level_counts[r.get("level", "?")] += 1
        status = r.get("status", 0)
        status_counts[status] += 1
        lat = r.get("latency_ms", 0)

        sampler_all.add(lat)

        if 500 <= status < 600:
            key = f"{r.get('method', '?')} {r.get('endpoint', '?')}"
            endpoint_5xx[key] += 1
            sampler_5xx.add(lat)
            err = r.get("error", "")
            if err:
                error_types[err] += 1

        # progreso cada 100k lineas (util para archivos grandes)
        if total % 100_000 == 0:
            print(f"  ... procesadas {total:,} lineas", flush=True)

    if total == 0:
        print("[ERROR]  No se encontraron registros validos.")
        return

    total_5xx    = sum(v for k, v in status_counts.items() if 500 <= k < 600)
    availability = (total - total_5xx) / total * 100
    error_rate   = total_5xx / total * 100
    slo_ok       = availability >= slo_target

    p50 = sampler_all.percentile(50)
    p95 = sampler_all.percentile(95)
    p99 = sampler_all.percentile(99)
    avg = sampler_all.avg()

    top_5xx = sorted(endpoint_5xx.items(), key=lambda x: x[1], reverse=True)[:5]

    SEP = "=" * 58
    print(SEP)
    print("  [LOG ANALYZER] — EPAM Scripting Exercise (streaming)")
    print(SEP)
    print(f"  Archivo        : {log_path}")
    print(f"  Total requests : {total:,}")
    print(f"  Reservoir size : {sample_size:,} (percentiles aproximados)")
    print(f"  INFO / WARN / ERROR : "
          f"{level_counts['INFO']:,} / {level_counts['WARN']:,} / {level_counts['ERROR']:,}")
    print()

    print("  [*]  Status code breakdown:")
    for code in sorted(status_counts):
        count = status_counts[code]
        bar   = "#" * (count * 28 // total)
        print(f"     {code}  {bar:<28} {count:>5}")
    print()

    print("  [t]  Latencia (reservoir sampling):")
    print(f"     avg={avg:.0f}ms   p50={p50:.0f}ms   p95={p95:.0f}ms   p99={p99:.0f}ms")
    if sampler_5xx.reservoir:
        p95_err = sampler_5xx.percentile(95)
        print(f"     p95 solo en 5xx: {p95_err:.0f}ms  (errores son mas lentos)")
    print()

    if top_5xx:
        print("  [!]  Top endpoints con errores 5xx:")
        for endpoint, count in top_5xx:
            print(f"     {count:>5}x  {endpoint}")
        print()

    if error_types:
        print("  [?]  Tipos de error:")
        for err, count in sorted(error_types.items(), key=lambda x: x[1], reverse=True):
            print(f"     {count:>5}x  {err}")
        print()

    slo_icon = "[OK]" if slo_ok else "[!!]"
    slo_msg  = "CUMPLIDO" if slo_ok else "VIOLADO — error budget agotado"
    print(f"  {slo_icon}  SLO {slo_target}% availability: {slo_msg}")
    print(f"     Error rate 5xx : {error_rate:.2f}%")
    print(f"     Availability   : {availability:.3f}%")
    if not slo_ok:
        deficit = slo_target - availability
        print(f"     Deficit        : {deficit:.3f}% bajo el objetivo")
        print(f"     -> En produccion dispara alerta de burn rate (lab-07/lab-09)")
    print(SEP)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analiza app.log JSON en modo streaming (memoria constante)"
    )
    parser.add_argument("--log",    type=str,   default="app.log", help="Ruta al log (default: app.log)")
    parser.add_argument("--slo",    type=float, default=99.5,      help="SLO objetivo %% availability (default: 99.5)")
    parser.add_argument("--sample", type=int,   default=10_000,    help="Tamano del reservoir para percentiles (default: 10000)")
    args = parser.parse_args()
    try:
        analyze_stream(args.log, args.slo, args.sample)
    except FileNotFoundError:
        print(f"[ERROR]  No se encontro '{args.log}'")
        print(f"   Genera uno primero con: python generate_logs.py")
