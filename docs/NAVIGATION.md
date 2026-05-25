# 🧭 Navegación de Documentación

> Mapa visual de cómo están conectados todos los documentos

---

## Flujo Secuencial

```
┌─────────────────────────────────────────────────────────────┐
│  00-concepts-overview.md                                    │
│  Mapa de conceptos — Léeme primero                          │
│  • La gran foto                                             │
│  • Kubernetes desde cero                                    │
│  • Ingress, Helm, EKS, IRSA                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  01-eks-ingress-alb.md                                      │
│  EKS + Ingress + ALB Controller                             │
│  • AWS Load Balancer Controller                             │
│  • Annotations del Ingress                                  │
│  • Troubleshooting                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  02-terraform-basics.md                                     │
│  Fundamentos de Terraform                                   │
│  • Providers, resources, variables                          │
│  • Ciclo de vida: init, plan, apply                         │
│  • State management básico                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  03-terraform-concepts.md                                   │
│  Terraform avanzado                                         │
│  • Remote state (S3 + DynamoDB)                             │
│  • Workspaces, for_each, dynamic blocks                     │
│  • Lifecycle rules                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  04-cicd-concepts.md                                        │
│  CI/CD con GitLab, Jenkins, AWS                             │
│  • GitLab CI/CD: stages, jobs, variables                    │
│  • GitLab OIDC                                              │
│  • Estrategias de deployment                                │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  05-observability-concepts.md                               │
│  Observabilidad: Métricas, Logs, Trazas                     │
│  • CloudWatch, Prometheus, Grafana                          │
│  • SLI/SLO dashboards                                       │
│  • PromQL básico                                            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  06-scripting-coding-prep.md                                │
│  Preparación para ejercicios de scripting                   │
│  • Patrones Python (streaming, parsing, boto3)              │
│  • Bash one-liners (jq, awk, cut, sort)                     │
│  • Troubleshooting de sistemas                              │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  07-kubernetes-deep-dive.md ⭐                              │
│  Kubernetes a profundidad                                   │
│  • Deployment vs ReplicaSet                                 │
│  • Namespaces, CronJob, Probes                              │
│  • Componentes Helm en EKS                                  │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  08-git-submodules-workflow.md ⭐                           │
│  Gestión de Git Submodules                                  │
│  • Por qué lab-11 está en GitLab                            │
│  • Cómo clonar y actualizar submódulos                      │
│  • Troubleshooting                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Navegación en Cada Documento

Todos los documentos tienen al final:

```markdown
## 📖 Navegación

- **⬅️ Anterior:** [documento-previo.md](./documento-previo.md)
- **➡️ Siguiente:** [documento-siguiente.md](./documento-siguiente.md)
- **🏠 Inicio:** [README.md](./README.md) — Índice de documentación
- **🔝 Volver al inicio:** [00-concepts-overview.md](./00-concepts-overview.md)
```

---

## Rutas de Lectura Recomendadas

### 🎯 Para Preparación de Entrevista (Prioridad)

```
07-kubernetes-deep-dive.md (PRIMERO)
    ↓
04-cicd-concepts.md
    ↓
05-observability-concepts.md
    ↓
06-scripting-coding-prep.md
    ↓
03-terraform-concepts.md
```

### 🌱 Para Principiantes (Desde Cero)

```
00-concepts-overview.md
    ↓
02-terraform-basics.md
    ↓
07-kubernetes-deep-dive.md
    ↓
01-eks-ingress-alb.md
    ↓
06-scripting-coding-prep.md
```

### 🔧 Para Troubleshooting

```
07-kubernetes-deep-dive.md (comandos de troubleshooting)
    ↓
01-eks-ingress-alb.md (problemas de Ingress)
    ↓
../troubleshooting/ (casos reales)
```

### 🛠️ Para Trabajar con el Repo

```
08-git-submodules-workflow.md (gestión de submódulos)
    ↓
../labs/lab-11-gitlab-oidc-mini/ (lab en GitLab)
```

---

## Conexiones entre Docs y Labs

### Observabilidad (docs/05 ↔ labs)

```
docs/05-observability-concepts.md
    ↓
    ├─→ labs/lab-07-monitoring/
    │   └─→ Prometheus + Grafana en EKS
    │       • kube-prometheus-stack
    │       • PromQL queries
    │       • Golden signals dashboards
    │
    ├─→ labs/lab-09-cloudwatch-logs/
    │   └─→ CloudWatch Logs + Metric Filters
    │       • EC2 con generador de logs
    │       • CloudWatch Agent
    │       • Logs Insights queries
    │
    └─→ labs/scripting/
        └─→ Análisis de logs con Python
            • log_analyzer.py
            • SLO check
            • Streaming de archivos grandes
```

### Scripting (docs/06 ↔ labs)

```
docs/06-scripting-coding-prep.md
    ↓
    ├─→ labs/scripting/
    │   └─→ 11 Mock Exercises
    │       • Python + Bash
    │       • warmup_exercises.md
    │       • bonus_practice.md
    │
    ├─→ labs/lab-09-cloudwatch-logs/
    │   └─→ Logs Insights queries
    │
    └─→ labs/lab-07-monitoring/
        └─→ PromQL queries
```

---

| Necesito... | Ir a... |
|-------------|---------|
| Entender Deployment vs ReplicaSet | [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md#1-deployment-vs-replicaset) |
| Configurar GitLab CI con OIDC | [04-cicd-concepts.md](./04-cicd-concepts.md) |
| Comandos de kubectl | [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md#7-comandos-esenciales-para-troubleshooting) |
| Remote state de Terraform | [03-terraform-concepts.md](./03-terraform-concepts.md) |
| Streaming en Python | [06-scripting-coding-prep.md](./06-scripting-coding-prep.md) |
| Trabajar con lab-11 | [08-git-submodules-workflow.md](./08-git-submodules-workflow.md) |
| Ingress no genera ALB | [01-eks-ingress-alb.md](./01-eks-ingress-alb.md) |
| SLI/SLO dashboards | [05-observability-concepts.md](./05-observability-concepts.md) |
| **Prometheus + Grafana en EKS** | [../labs/lab-07-monitoring/Readme.md](../labs/lab-07-monitoring/Readme.md) |
| **CloudWatch Logs + Metric Filters** | [../labs/lab-09-cloudwatch-logs/Readme.md](../labs/lab-09-cloudwatch-logs/Readme.md) |
| **Ejercicios de Scripting** | [../labs/scripting/README.md](../labs/scripting/README.md) |

---

## Estructura Completa del Repo

```
epam-aws-devops-prep/
│
├── docs/                        ← ESTÁS AQUÍ
│   ├── README.md                ← Índice principal
│   ├── NAVIGATION.md            ← Este archivo
│   ├── 00-concepts-overview.md
│   ├── 01-eks-ingress-alb.md
│   ├── 02-terraform-basics.md
│   ├── 03-terraform-concepts.md
│   ├── 04-cicd-concepts.md
│   ├── 05-observability-concepts.md
│   ├── 06-scripting-coding-prep.md
│   ├── 07-kubernetes-deep-dive.md
│   └── 08-git-submodules-workflow.md
│
├── prep/                        ← Material de preparación
│   ├── INTERVIEW-PREP-2PM.md
│   └── CHEATSHEET-1PAGE.md
│
├── labs/                        ← Labs prácticos
│   ├── lab-01-vpc/
│   ├── lab-02-iam/
│   ├── ...
│   └── scripting/
│
└── troubleshooting/             ← Casos reales
    ├── 01-librechat-ingress.md
    ├── 02-jwt-dst-incident.md
    └── ...
```

---

## Cómo Usar Este Sistema de Navegación

### 1. Lectura Secuencial

Si quieres leer todo en orden:

```bash
# Empezar desde el principio
cat docs/00-concepts-overview.md

# Al final verás:
# ➡️ Siguiente: 01-eks-ingress-alb.md

# Seguir al siguiente
cat docs/01-eks-ingress-alb.md

# Y así sucesivamente...
```

### 2. Lectura por Tema

Si buscas un tema específico:

```bash
# Ver el índice
cat docs/README.md

# Ir directamente al documento que necesitas
cat docs/07-kubernetes-deep-dive.md
```

### 3. Navegación Rápida

Usa los links al final de cada documento:

- **⬅️ Anterior** — Si quieres repasar el tema previo
- **➡️ Siguiente** — Para continuar en orden
- **🏠 Inicio** — Para ver el índice completo
- **🔝 Volver al inicio** — Para ir al documento 00

---

## Tips de Navegación

### En VS Code

```bash
# Abrir todos los docs en tabs
code docs/*.md

# Usar Ctrl+Tab para navegar entre tabs
# Usar Ctrl+Click en los links para abrir
```

### En Terminal

```bash
# Ver el índice
cat docs/README.md

# Leer un documento con paginación
less docs/07-kubernetes-deep-dive.md

# Buscar en todos los docs
grep -r "Deployment" docs/
```

### En GitHub

- Los links funcionan automáticamente
- Puedes navegar haciendo click
- GitHub renderiza el markdown con formato

---

## Feedback

Si encuentras un link roto o una navegación confusa:

1. Verifica que el archivo existe
2. Revisa que el path sea correcto (`./ ` para mismo directorio)
3. Abre un issue o corrige directamente

---

**Última actualización:** 2026-04-13
