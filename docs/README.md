# 📖 Documentación Conceptual

Esta carpeta contiene documentación detallada de conceptos técnicos necesarios para la entrevista EPAM DevOps/SRE.

**🧭 [Ver mapa de navegación completo](./NAVIGATION.md)** — Cómo están conectados todos los documentos

---

## 📚 Índice de Documentos

### Flujo de Lectura Secuencial

```
00-concepts-overview.md (Mapa de conceptos)
    ↓
01-eks-ingress-alb.md (EKS + Ingress + ALB)
    ↓
02-terraform-basics.md (Fundamentos de Terraform)
    ↓
03-terraform-concepts.md (Terraform avanzado)
    ↓
04-cicd-concepts.md (CI/CD)
    ↓
05-observability-concepts.md (Observabilidad)
    ↓
06-scripting-coding-prep.md (Scripting)
    ↓
07-kubernetes-deep-dive.md (Kubernetes profundo)
    ↓
08-git-submodules-workflow.md (Git Submodules)
```

**💡 Cada documento tiene navegación al final:**
- ⬅️ Anterior — Documento previo
- ➡️ Siguiente — Documento siguiente
- 🏠 Inicio — Volver a este índice
- 🔝 Volver al inicio — Ir al documento 00

---

### [00-concepts-overview.md](./00-concepts-overview.md)
**Mapa de conceptos — Léeme primero**

- La gran foto: cómo encaja todo
- Kubernetes desde cero
- Ingress, Annotations, Helm
- EKS, IRSA, Karpenter
- Flujo completo de una request HTTP
- Preguntas de entrevista con esquema de respuesta

**Cuándo leer:** Antes de empezar cualquier lab. Es tu punto de entrada.

---

### [01-eks-ingress-alb.md](./01-eks-ingress-alb.md)
**EKS + Ingress + ALB Controller**

- Cómo funciona el AWS Load Balancer Controller
- Annotations del Ingress para ALB
- Troubleshooting de Ingress que no genera ALB
- Target Groups y health checks

**Cuándo leer:** Antes de trabajar con Ingress en EKS.

---

### [02-terraform-basics.md](./02-terraform-basics.md)
**Fundamentos de Terraform**

- Providers, resources, variables, outputs
- Ciclo de vida: init, plan, apply, destroy
- State management básico
- Módulos simples

**Cuándo leer:** Antes de empezar labs de Terraform.

---

### [03-terraform-concepts.md](./03-terraform-concepts.md)
**Conceptos avanzados de Terraform**

- Remote state (S3 + DynamoDB)
- Workspaces para múltiples ambientes
- for_each vs count
- Dynamic blocks
- Lifecycle rules (create_before_destroy, prevent_destroy)

**Cuándo leer:** Después de dominar los básicos de Terraform.

---

### [04-cicd-concepts.md](./04-cicd-concepts.md)
**CI/CD con GitLab, Jenkins, AWS CodePipeline**

- GitLab CI/CD: stages, jobs, variables, artifacts
- GitLab OIDC para autenticación con AWS
- Estrategias de deployment (Blue/Green, Canary, Rolling)
- Seguridad en pipelines (Trivy, SAST)

**Cuándo leer:** Antes de configurar pipelines de CI/CD.

---

### [05-observability-concepts.md](./05-observability-concepts.md)
**Observabilidad: Métricas, Logs, Trazas**

- Los 3 pilares de observabilidad
- CloudWatch: métricas, logs, alarms, Logs Insights
- Prometheus + Grafana: PromQL, scraping, alertmanager
- Datadog, Splunk
- SLI/SLO dashboards

**Cuándo leer:** Antes de configurar monitoring en EKS.

---

### [06-scripting-coding-prep.md](./06-scripting-coding-prep.md)
**Preparación para ejercicios de scripting**

- Patrones comunes en Python (streaming, parsing, boto3)
- Bash one-liners (jq, awk, cut, sort)
- Troubleshooting de sistemas (disk, CPU, memory, network)
- Kubernetes troubleshooting (CrashLoopBackOff, OOMKilled)

**Cuándo leer:** Antes de practicar ejercicios de scripting en [../labs/scripting/](../labs/scripting/).

---

### [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md) ⭐ **NUEVO**
**Kubernetes a profundidad**

- **Deployment vs ReplicaSet** (con diagramas, rolling updates, rollbacks)
- **Namespaces** (qué son, para qué sirven, DNS, RBAC, quotas)
- **CronJob** (tareas programadas, sintaxis de schedule)
- **Componentes Helm en EKS** (ALB Controller, Prometheus, Fluent Bit, Secrets CSI, etc.)
- **Probes** (liveness, readiness, startup)
- **StatefulSet, DaemonSet, Job**
- **Comandos esenciales de troubleshooting**
- **Respuestas rápidas para entrevista**

**Cuándo leer:** Antes de la entrevista técnica. Cubre los conceptos que te preguntaron en la entrevista EPAM.

---

### [08-git-submodules-workflow.md](./08-git-submodules-workflow.md) ⭐ **NUEVO**
**Gestión de Git Submodules**

- Por qué el lab-11 está en GitLab como submódulo
- Cómo clonar el repo con submódulos
- Cómo actualizar y sincronizar el submódulo
- Troubleshooting de problemas comunes
- Alternativas consideradas y por qué se eligió submodule
- Best practices para trabajar con submódulos

**Cuándo leer:** Si vas a trabajar con el lab-11 o necesitas entender la estructura de dos repos.

---

## 🎯 Orden de Lectura Recomendado

### Para principiantes
1. [00-concepts-overview.md](./00-concepts-overview.md) — La gran foto
2. [02-terraform-basics.md](./02-terraform-basics.md) — Fundamentos de IaC
3. [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md) — Kubernetes esencial
4. [01-eks-ingress-alb.md](./01-eks-ingress-alb.md) — Ingress en EKS
5. [06-scripting-coding-prep.md](./06-scripting-coding-prep.md) — Scripting

### Para preparación de entrevista
1. [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md) — **PRIORIDAD**
2. [04-cicd-concepts.md](./04-cicd-concepts.md) — GitLab CI/CD
3. [05-observability-concepts.md](./05-observability-concepts.md) — Monitoring
4. [06-scripting-coding-prep.md](./06-scripting-coding-prep.md) — Scripting
5. [03-terraform-concepts.md](./03-terraform-concepts.md) — Terraform avanzado

### Para troubleshooting
1. [07-kubernetes-deep-dive.md](./07-kubernetes-deep-dive.md) — Comandos de troubleshooting
2. [01-eks-ingress-alb.md](./01-eks-ingress-alb.md) — Problemas de Ingress
3. [../troubleshooting/](../troubleshooting/) — Casos reales

---

## 🔗 Recursos Relacionados

- **Labs prácticos:** [../labs/](../labs/)
- **Preparación de entrevista:** [../prep/](../prep/)
- **Casos de troubleshooting:** [../troubleshooting/](../troubleshooting/)
- **Notas personales:** [../notes/](../notes/)

---

## 📝 Cómo Contribuir

Si encuentras errores o quieres agregar contenido:

1. Edita el archivo correspondiente
2. Mantén el formato consistente (títulos, código, ejemplos)
3. Agrega ejemplos prácticos cuando sea posible
4. Incluye comandos que se puedan copiar y pegar

---

**Última actualización:** 2026-04-13
