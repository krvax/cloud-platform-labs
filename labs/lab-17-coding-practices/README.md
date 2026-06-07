# Lab 17 — Python Coding Practices (12-Factor, SOLID, DRY)

> **Objetivo:** Practicar los principios que Bridgewater señaló como gap.
> **Tiempo:** ~45 min total (3 ejercicios de 15 min cada uno)
> **Prerequisitos:** Python 3.10+, acceso a terminal

---

## Ejercicio 01: De Script Monolítico a 12-Factor + SOLID

**Escenario:** Tienes un script que lee un archivo de logs, filtra errores, y envía un resumen por webhook. Todo en un solo archivo, todo hardcodeado.

### El "antes" (anti-patrón):

```python
# bad_script.py — NO HAGAS ESTO
import requests

def main():
    # Config hardcoded (viola Factor 3)
    log_file = "/var/log/app.log"
    webhook = "https://hooks.slack.com/services/XXX/YYY/ZZZ"
    
    # Lee, filtra Y notifica en una función (viola SRP)
    errors = []
    with open(log_file) as f:
        for line in f:
            if "ERROR" in line:
                errors.append(line.strip())
    
    # Retry logic duplicada (viola DRY)
    for i in range(3):
        try:
            requests.post(webhook, json={"text": f"Found {len(errors)} errors:\n" + "\n".join(errors[:5])})
            break
        except:
            pass

if __name__ == "__main__":
    main()
```

### Tu tarea: Reescríbelo aplicando:
1. **12-Factor (Config):** Config desde env vars
2. **SOLID (SRP):** Separar en funciones/clases con responsabilidad única
3. **SOLID (DIP):** Inyectar dependencias
4. **DRY:** Extraer retry como decorator

### Solución guía → `exercises/01_refactored/`

---

## Ejercicio 02: Terraform DRY — Módulos Parametrizados

**Escenario:** Tienes Terraform duplicado para dev y prod. Refactoriza a módulos.

### El "antes" (anti-patrón):
```
infra/
├── dev/
│   └── main.tf    ← 80 líneas, casi idéntico a prod
└── prod/
    └── main.tf    ← 80 líneas, casi idéntico a dev
```

### Tu tarea: Refactoriza a:
```
infra/
├── modules/
│   └── app/
│       ├── main.tf
│       ├── variables.tf
│       └── outputs.tf
├── envs/
│   ├── dev.tfvars
│   └── prod.tfvars
└── main.tf          ← llama al módulo
```

### Solución guía → `exercises/02_terraform_dry/`

---

## Ejercicio 03: Pipeline de Observabilidad (SOLID en Python)

**Escenario:** Diseña un mini pipeline de métricas que siga SOLID.

### Requisitos:
- Collector: lee métricas de un archivo/endpoint
- Processor: filtra/agrega
- Exporter: envía a stdout (mock de Prometheus/Datadog)
- Cada componente es intercambiable (Open/Closed, DIP)

### Solución guía → `exercises/03_observability_pipeline/`
