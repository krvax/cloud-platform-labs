# 🔥 Warm-Up Exercises — Pre-Interview Practice

> **Cronométrate:** 20 minutos total para los 3 ejercicios  
> **Regla:** No mires tus scripts existentes ni el README  
> **Objetivo:** Activar tu memoria muscular antes de la entrevista

---

## Setup

```bash
cd ~/src/learning/EPAM/epam-aws-devops-prep/labs/scripting

# Genera datos frescos
python generate_logs.py --lines 2000

# Crea archivos de trabajo
touch warmup1.py warmup2.sh warmup3.py
```

---

## Exercise 1: Error Rate Calculator (Python, 7 min)

### Prompt
Escribe un script `warmup1.py` que:
1. Lea `app.log` línea por línea (streaming)
2. Cuente total de requests
3. Cuente requests con status >= 500
4. Calcule error rate como porcentaje
5. Imprima si cumple SLO de 99.5% availability
6. Exit code 0 si cumple SLO, 1 si no

### Requisitos técnicos
- Usa `with open()` y `for line in f` (streaming)
- Maneja `json.JSONDecodeError` sin crashear
- Usa `argparse` para `--log` y `--slo`
- Imprime resultado claro

### Test
```bash
python warmup1.py --log app.log --slo 99.5
# Debe imprimir algo como:
# Total: 2000
# Errors 5xx: 140
# Error rate: 7.00%
# Availability: 93.00%
# SLO 99.5%: FAIL

echo $?  # debe ser 1 (porque no cumple SLO)
```

### Tiempo: 7 minutos ⏱️

---

## Exercise 2: Top Endpoints (Bash, 5 min)

### Prompt
Escribe un one-liner bash en `warmup2.sh` que:
1. Extraiga el campo `endpoint` de cada línea JSON
2. Cuente cuántas veces aparece cada endpoint
3. Ordene de mayor a menor
4. Muestre solo el top 5

### Requisitos técnicos
- Usa `jq`, `sort`, `uniq -c`, `head`
- Debe ser UN solo comando (puedes usar pipes)

### Test
```bash
bash warmup2.sh
# Debe imprimir algo como:
#     280 /health
#     240 /search
#     220 /items
#     ...
```

### Tiempo: 5 minutos ⏱️

---

## Exercise 3: Version Sorter (Python, 8 min)

### Prompt
Escribe un script `warmup3.py` que:
1. Acepte una lista de versiones como argumentos: `python warmup3.py 1.10.1 1.9.4 2.0.0 1.2.3`
2. Las ordene correctamente (version sort, no alfabético)
3. Imprima la lista ordenada, una por línea
4. Imprima al final: "Oldest: X.X.X" y "Newest: X.X.X"

### Requisitos técnicos
- Usa `sys.argv` o `argparse`
- Convierte versiones a tuplas de ints para comparar
- Maneja el caso de 0 argumentos

### Test
```bash
python warmup3.py 1.10.1 1.9.4 2.0.0 1.2.3
# Debe imprimir:
# 1.2.3
# 1.9.4
# 1.10.1
# 2.0.0
# Oldest: 1.2.3
# Newest: 2.0.0
```

### Tiempo: 8 minutos ⏱️

---

## Soluciones (No Mires Hasta Terminar)

<details>
<summary>💡 Solución Exercise 1</summary>

```python
#!/usr/bin/env python3
"""warmup1.py — Error rate calculator"""
import json
import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--log", default="app.log")
    parser.add_argument("--slo", type=float, default=99.5)
    args = parser.parse_args()

    total = 0
    errors_5xx = 0

    try:
        with open(args.log) as f:
            for line in f:
                try:
                    r = json.loads(line)
                    total += 1
                    if r.get("status", 0) >= 500:
                        errors_5xx += 1
                except json.JSONDecodeError:
                    continue
    except FileNotFoundError:
        print(f"ERROR: {args.log} not found", file=sys.stderr)
        sys.exit(1)

    if total == 0:
        print("No records found")
        sys.exit(1)

    error_rate = errors_5xx / total * 100
    availability = 100 - error_rate
    slo_ok = availability >= args.slo

    print(f"Total: {total}")
    print(f"Errors 5xx: {errors_5xx}")
    print(f"Error rate: {error_rate:.2f}%")
    print(f"Availability: {availability:.2f}%")
    print(f"SLO {args.slo}%: {'PASS' if slo_ok else 'FAIL'}")

    sys.exit(0 if slo_ok else 1)

if __name__ == "__main__":
    main()
```
</details>

<details>
<summary>💡 Solución Exercise 2</summary>

```bash
#!/bin/bash
# warmup2.sh — Top 5 endpoints

jq -r '.endpoint' app.log | sort | uniq -c | sort -nr | head -5
```

**Explicación:**
- `jq -r '.endpoint'` → extrae campo endpoint, raw output (sin comillas)
- `sort` → ordena alfabéticamente (necesario para uniq)
- `uniq -c` → cuenta ocurrencias consecutivas
- `sort -nr` → ordena numérico reverso (mayor primero)
- `head -5` → top 5
</details>

<details>
<summary>💡 Solución Exercise 3</summary>

```python
#!/usr/bin/env python3
"""warmup3.py — Version sorter"""
import sys

def main():
    if len(sys.argv) < 2:
        print("Usage: python warmup3.py <version1> <version2> ...")
        sys.exit(1)

    versions = sys.argv[1:]
    
    # Convertir "1.10.1" → (1, 10, 1) para comparación correcta
    sorted_versions = sorted(versions, key=lambda v: tuple(map(int, v.split("."))))

    for v in sorted_versions:
        print(v)
    
    print(f"Oldest: {sorted_versions[0]}")
    print(f"Newest: {sorted_versions[-1]}")

if __name__ == "__main__":
    main()
```

**Explicación:**
- `sys.argv[1:]` → todos los argumentos excepto el nombre del script
- `lambda v: tuple(map(int, v.split(".")))` → "1.10.1" → (1, 10, 1)
- Python compara tuplas elemento por elemento → (1, 10, 1) > (1, 9, 4)
</details>

---

## Auto-Evaluación

### ✅ Si terminaste en < 20 min y todo funciona:
**Estás listo.** Tienes la memoria muscular activada.

### ⚠️ Si te tomó 20-30 min:
**Bien.** Repasa los conceptos del INTERVIEW-PREP-2PM.md.

### ❌ Si te tomó > 30 min o no funcionó:
**No te preocupes.** Revisa las soluciones, entiende el patrón, y hazlos de nuevo.

---

## Conceptos Clave Practicados

| Exercise | Concepto | Por qué importa |
|----------|----------|-----------------|
| 1 | Streaming con `for line in f` | Memoria constante, archivos grandes |
| 1 | Error handling con try/except | Scripts robustos en producción |
| 1 | Exit codes (0 vs 1) | Útil en CI/CD pipelines |
| 2 | jq + pipes | Análisis rápido de logs JSON |
| 2 | sort \| uniq -c \| sort -nr | Patrón común en troubleshooting |
| 3 | Version sort con tuplas | Evita bug clásico de sort alfabético |
| 3 | sys.argv | Scripts CLI básicos |

---

## Next Steps

1. **Si terminaste rápido:** Haz el Mock 7 del README (streaming avanzado)
2. **Si te costó:** Repasa el INTERVIEW-PREP-2PM.md
3. **30 min antes de la entrevista:** Respira, toma agua, repasa frases en inglés

**¡Éxito!** 🚀
