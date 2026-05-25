# 07 — Kubernetes Deep Dive

> Conceptos fundamentales de Kubernetes que debes dominar para entrevistas EPAM DevOps/SRE

---

## 1. Deployment vs ReplicaSet

### ¿Qué es un ReplicaSet?

```
ReplicaSet
├── Garantiza que N réplicas de un pod estén corriendo
├── Si un pod muere, crea otro automáticamente
├── Usa un selector para identificar qué pods controla
└── NO sabe hacer rolling updates
```

**Ejemplo de ReplicaSet:**

```yaml
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: catalog-rs
spec:
  replicas: 3
  selector:
    matchLabels:
      app: catalog
  template:
    metadata:
      labels:
        app: catalog
    spec:
      containers:
      - name: catalog
        image: catalog:v1
        ports:
        - containerPort: 8080
```

**Problema:** Si cambias la imagen a `catalog:v2` y haces `kubectl apply`, el ReplicaSet NO actualiza los pods existentes. Solo crea nuevos pods con v2 si un pod muere.

---

### ¿Qué es un Deployment?

```
Deployment (lo que TÚ creas)
├── Es un wrapper ENCIMA de ReplicaSet
├── Agrega: rolling updates, rollbacks, versioning
├── Mantiene historial de ReplicaSets
└── Estrategias: RollingUpdate, Recreate
```

**Jerarquía:**

```
Deployment: catalog-deployment
│
├── ReplicaSet: catalog-deployment-7d4f8c9b (v1) ← viejo, 0 réplicas
│   ├── Pod: catalog-7d4f8c9b-abc12 (terminado)
│   ├── Pod: catalog-7d4f8c9b-def34 (terminado)
│   └── Pod: catalog-7d4f8c9b-ghi56 (terminado)
│
└── ReplicaSet: catalog-deployment-9f6a2e1d (v2) ← nuevo, 3 réplicas
    ├── Pod: catalog-9f6a2e1d-xyz78 (running)
    ├── Pod: catalog-9f6a2e1d-uvw90 (running)
    └── Pod: catalog-9f6a2e1d-rst12 (running)
```

**Ejemplo de Deployment:**

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: catalog-deployment
spec:
  replicas: 3
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1        # máximo 1 pod extra durante update
      maxUnavailable: 0  # siempre mantén 3 pods disponibles
  selector:
    matchLabels:
      app: catalog
  template:
    metadata:
      labels:
        app: catalog
    spec:
      containers:
      - name: catalog
        image: catalog:v2  # ← cambias esto
        ports:
        - containerPort: 8080
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
```

---

### ¿Qué pasa cuando actualizas un Deployment?

```bash
# 1. Cambias la imagen en el YAML
kubectl set image deployment/catalog-deployment catalog=catalog:v2

# 2. Kubernetes hace esto automáticamente:
```

```
Paso 1: Deployment crea ReplicaSet-v2 con 0 réplicas
Paso 2: Sube 1 pod en ReplicaSet-v2 (maxSurge: 1)
Paso 3: Espera a que el pod esté Ready (readinessProbe)
Paso 4: Baja 1 pod en ReplicaSet-v1
Paso 5: Repite hasta que ReplicaSet-v2 tenga 3 réplicas
Paso 6: ReplicaSet-v1 queda con 0 réplicas (pero NO se borra)
```

**Rollback:**

```bash
# Ver historial
kubectl rollout history deployment/catalog-deployment

# Volver a la versión anterior
kubectl rollout undo deployment/catalog-deployment

# Volver a una versión específica
kubectl rollout undo deployment/catalog-deployment --to-revision=2
```

---

### Comparación Rápida

| Característica | ReplicaSet | Deployment |
|----------------|------------|------------|
| Mantiene N réplicas | ✅ | ✅ |
| Self-healing (recrea pods) | ✅ | ✅ |
| Rolling updates | ❌ | ✅ |
| Rollback | ❌ | ✅ |
| Historial de versiones | ❌ | ✅ |
| Estrategias de deploy | ❌ | ✅ |
| **Cuándo usarlo** | Nunca directamente | Siempre |

**Regla de oro:** SIEMPRE usa Deployment. NUNCA crees ReplicaSet directamente.

---

## 2. Namespaces

### ¿Qué es un Namespace?

```
Un namespace es una división lógica dentro del cluster de Kubernetes.
Es como tener "carpetas" para organizar y aislar recursos.
```

**Estructura típica:**

```
Cluster EKS: my-cluster
│
├── namespace: dev
│   ├── deployment/catalog
│   ├── deployment/shopping
│   ├── deployment/orders
│   ├── service/catalog-svc
│   └── ingress/app-ingress
│
├── namespace: staging
│   ├── deployment/catalog
│   ├── deployment/shopping
│   └── deployment/orders
│
├── namespace: production
│   ├── deployment/catalog
│   ├── deployment/shopping
│   ├── deployment/orders
│   └── configmap/app-config
│
├── namespace: monitoring
│   ├── deployment/prometheus
│   ├── deployment/grafana
│   └── service/prometheus-svc
│
└── namespace: kube-system  ← componentes internos de K8s
    ├── deployment/coredns
    ├── daemonset/kube-proxy
    └── deployment/aws-load-balancer-controller
```

---

### ¿Para qué sirven los Namespaces?

#### 1. Organización

```bash
# Agrupar recursos por equipo, ambiente o aplicación
kubectl get pods -n production
kubectl get pods -n dev
kubectl get pods -n monitoring
```

#### 2. Aislamiento

```yaml
# Network Policy: solo pods en "production" pueden hablar entre sí
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: deny-from-other-namespaces
  namespace: production
spec:
  podSelector: {}
  policyTypes:
  - Ingress
  ingress:
  - from:
    - podSelector: {}  # solo pods del mismo namespace
```

#### 3. Resource Quotas

```yaml
# Limitar CPU/memoria por namespace
apiVersion: v1
kind: ResourceQuota
metadata:
  name: dev-quota
  namespace: dev
spec:
  hard:
    requests.cpu: "10"
    requests.memory: 20Gi
    limits.cpu: "20"
    limits.memory: 40Gi
    pods: "50"
```

#### 4. RBAC (Control de Acceso)

```yaml
# Dar permisos solo a cierto namespace
apiVersion: rbac.authorization.k8s.io/v1
kind: RoleBinding
metadata:
  name: dev-team-binding
  namespace: dev
subjects:
- kind: Group
  name: dev-team
  apiGroup: rbac.authorization.k8s.io
roleRef:
  kind: Role
  name: developer
  apiGroup: rbac.authorization.k8s.io
```

#### 5. Nombres sin conflicto

```bash
# Puedes tener "catalog" en dev Y en prod sin conflicto
kubectl get deployment catalog -n dev
kubectl get deployment catalog -n production
```

---

### Comandos Básicos

```bash
# Listar namespaces
kubectl get namespaces
kubectl get ns

# Crear namespace
kubectl create namespace staging

# Ver recursos en un namespace
kubectl get pods -n production
kubectl get all -n production

# Ver recursos en TODOS los namespaces
kubectl get pods --all-namespaces
kubectl get pods -A

# Cambiar namespace por defecto (para no escribir -n siempre)
kubectl config set-context --current --namespace=production

# Describir namespace
kubectl describe namespace production

# Borrar namespace (CUIDADO: borra TODO dentro)
kubectl delete namespace dev
```

---

### DNS entre Namespaces

Los servicios tienen DNS automático:

```
<service-name>.<namespace>.svc.cluster.local
```

**Ejemplo:**

```yaml
# Service en namespace "production"
apiVersion: v1
kind: Service
metadata:
  name: catalog-svc
  namespace: production
spec:
  selector:
    app: catalog
  ports:
  - port: 8080
```

**Desde otro pod en el MISMO namespace:**

```bash
curl http://catalog-svc:8080
```

**Desde otro pod en DIFERENTE namespace:**

```bash
curl http://catalog-svc.production.svc.cluster.local:8080
```

---

### Namespaces por Defecto

Kubernetes crea estos namespaces automáticamente:

| Namespace | Propósito |
|-----------|-----------|
| `default` | Namespace por defecto si no especificas otro |
| `kube-system` | Componentes internos de Kubernetes (DNS, proxy, etc.) |
| `kube-public` | Recursos públicos, legibles por todos |
| `kube-node-lease` | Heartbeats de nodos (para detectar nodos caídos) |

---

## 3. CronJob — Tareas Programadas

### ¿Qué es un CronJob?

```
CronJob = cron de Linux + Kubernetes
Ejecuta un Job en un horario específico (como crontab)
```

**Caso de uso:** Actualizar catálogo cada 30 minutos

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: catalog-sync
  namespace: production
spec:
  schedule: "*/30 * * * *"  # cada 30 minutos
  successfulJobsHistoryLimit: 3
  failedJobsHistoryLimit: 1
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: sync
            image: my-app/catalog-sync:latest
            env:
            - name: CATALOG_API
              value: "http://catalog-svc:8080"
            - name: SOURCE_URL
              value: "https://external-api.com/catalog"
          restartPolicy: OnFailure
```

**Sintaxis de schedule (igual que cron):**

```
┌───────────── minuto (0 - 59)
│ ┌───────────── hora (0 - 23)
│ │ ┌───────────── día del mes (1 - 31)
│ │ │ ┌───────────── mes (1 - 12)
│ │ │ │ ┌───────────── día de la semana (0 - 6) (Domingo=0)
│ │ │ │ │
* * * * *
```

**Ejemplos:**

```bash
"0 2 * * *"       # Todos los días a las 2:00 AM
"*/15 * * * *"    # Cada 15 minutos
"0 */6 * * *"     # Cada 6 horas
"0 9 * * 1"       # Lunes a las 9:00 AM
"0 0 1 * *"       # Primer día del mes a medianoche
```

**Comandos:**

```bash
# Ver CronJobs
kubectl get cronjobs -n production

# Ver Jobs creados por el CronJob
kubectl get jobs -n production

# Ver logs del último Job
kubectl logs -n production job/catalog-sync-28471234

# Ejecutar manualmente (sin esperar el schedule)
kubectl create job --from=cronjob/catalog-sync manual-sync-1 -n production
```

---

## 4. Componentes que se instalan con Helm en EKS

### Lista Completa para Entrevista

```bash
# 1. AWS Load Balancer Controller (OBLIGATORIO para Ingress)
helm repo add eks https://aws.github.io/eks-charts
helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  --namespace kube-system \
  --set clusterName=my-cluster \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

# 2. Monitoring: Prometheus + Grafana
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring --create-namespace

# 3. Logging: Fluent Bit → CloudWatch Logs
helm repo add eks https://aws.github.io/eks-charts
helm install aws-for-fluent-bit eks/aws-for-fluent-bit \
  --namespace kube-system \
  --set cloudWatch.region=us-east-1 \
  --set cloudWatch.logGroupName=/aws/eks/my-cluster/logs

# 4. Secrets: AWS Secrets Manager + Secrets Store CSI Driver
helm repo add secrets-store-csi-driver https://kubernetes-sigs.github.io/secrets-store-csi-driver/charts
helm install secrets-store-csi-driver secrets-store-csi-driver/secrets-store-csi-driver \
  --namespace kube-system

# 5. Cert Manager (para TLS automático con Let's Encrypt)
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# 6. External DNS (actualiza Route53 automáticamente)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install external-dns bitnami/external-dns \
  --namespace kube-system \
  --set provider=aws \
  --set aws.region=us-east-1

# 7. Metrics Server (para kubectl top y HPA)
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system

# 8. Ingress NGINX (alternativa al ALB Controller)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

---

### Tabla Resumen

| Componente | Para qué sirve | Namespace típico |
|------------|----------------|------------------|
| AWS Load Balancer Controller | Crear ALB/NLB desde Ingress | kube-system |
| Prometheus + Grafana | Métricas y dashboards | monitoring |
| Fluent Bit | Enviar logs a CloudWatch | kube-system |
| Secrets Store CSI Driver | Montar secrets de AWS Secrets Manager | kube-system |
| Cert Manager | Certificados TLS automáticos | cert-manager |
| External DNS | Actualizar Route53 automáticamente | kube-system |
| Metrics Server | `kubectl top`, HPA | kube-system |
| Ingress NGINX | Ingress Controller alternativo | ingress-nginx |

---

## 5. Probes — Liveness vs Readiness

### Liveness Probe

```
¿El contenedor está vivo?
Si falla → Kubernetes MATA el pod y crea uno nuevo
```

**Cuándo usar:** Detectar deadlocks, procesos colgados

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30  # espera 30s antes de empezar a chequear
  periodSeconds: 10        # chequea cada 10s
  timeoutSeconds: 5        # timeout de 5s
  failureThreshold: 3      # 3 fallos consecutivos → mata el pod
```

---

### Readiness Probe

```
¿El contenedor está listo para recibir tráfico?
Si falla → Kubernetes QUITA el pod del Service (no recibe requests)
         → Pero NO mata el pod
```

**Cuándo usar:** Esperar a que la app termine de inicializar (DB connections, cache warmup)

```yaml
readinessProbe:
  httpGet:
    path: /ready
    port: 8080
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 2
```

---

### Startup Probe (Bonus)

```
¿El contenedor terminó de arrancar?
Si falla → Kubernetes MATA el pod
Útil para apps que tardan mucho en iniciar
```

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  initialDelaySeconds: 0
  periodSeconds: 10
  failureThreshold: 30  # 30 intentos × 10s = 5 minutos máximo
```

---

### Tipos de Probes

```yaml
# 1. HTTP GET
livenessProbe:
  httpGet:
    path: /health
    port: 8080
    httpHeaders:
    - name: Custom-Header
      value: Awesome

# 2. TCP Socket
livenessProbe:
  tcpSocket:
    port: 8080

# 3. Exec (comando)
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
```

---

### Ejemplo Completo

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: catalog
spec:
  replicas: 3
  selector:
    matchLabels:
      app: catalog
  template:
    metadata:
      labels:
        app: catalog
    spec:
      containers:
      - name: catalog
        image: catalog:v2
        ports:
        - containerPort: 8080
        
        # Startup: espera hasta 5 min a que arranque
        startupProbe:
          httpGet:
            path: /startup
            port: 8080
          periodSeconds: 10
          failureThreshold: 30
        
        # Liveness: si falla 3 veces, mata el pod
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          failureThreshold: 3
        
        # Readiness: si falla, quita del Service
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          failureThreshold: 2
        
        resources:
          requests:
            cpu: 100m
            memory: 128Mi
          limits:
            cpu: 500m
            memory: 512Mi
```

---

## 6. Otros Recursos Importantes

### StatefulSet

```
Para aplicaciones con estado (bases de datos, colas)
- Pods tienen identidad estable (catalog-0, catalog-1, catalog-2)
- Volúmenes persistentes por pod
- Orden garantizado en deploy/scale
```

**Cuándo usar:** PostgreSQL, Redis, Kafka, Elasticsearch

---

### DaemonSet

```
Ejecuta 1 pod en CADA nodo del cluster
```

**Cuándo usar:** Logging agents, monitoring agents, network plugins

```yaml
apiVersion: apps/v1
kind: DaemonSet
metadata:
  name: fluentd
spec:
  selector:
    matchLabels:
      app: fluentd
  template:
    metadata:
      labels:
        app: fluentd
    spec:
      containers:
      - name: fluentd
        image: fluentd:latest
```

---

### Job

```
Ejecuta una tarea hasta completarla (no es un servicio continuo)
```

**Cuándo usar:** Migraciones de DB, batch processing

```yaml
apiVersion: batch/v1
kind: Job
metadata:
  name: db-migration
spec:
  template:
    spec:
      containers:
      - name: migrate
        image: my-app/migrate:latest
        command: ["python", "migrate.py"]
      restartPolicy: OnFailure
  backoffLimit: 4  # reintentar hasta 4 veces
```

---

## 7. Comandos Esenciales para Troubleshooting

```bash
# Ver pods con más detalle
kubectl get pods -o wide -n production

# Describir pod (eventos, estado)
kubectl describe pod catalog-9f6a2e1d-xyz78 -n production

# Logs
kubectl logs catalog-9f6a2e1d-xyz78 -n production
kubectl logs -f catalog-9f6a2e1d-xyz78 -n production  # follow
kubectl logs --previous catalog-9f6a2e1d-xyz78        # logs del pod anterior (si crasheó)

# Ejecutar comando dentro del pod
kubectl exec -it catalog-9f6a2e1d-xyz78 -n production -- /bin/bash
kubectl exec catalog-9f6a2e1d-xyz78 -n production -- curl localhost:8080/health

# Ver endpoints (qué pods están detrás del Service)
kubectl get endpoints catalog-svc -n production

# Ver eventos del cluster
kubectl get events -n production --sort-by='.lastTimestamp'

# Port forward (para debugging)
kubectl port-forward pod/catalog-9f6a2e1d-xyz78 8080:8080 -n production

# Ver uso de recursos
kubectl top nodes
kubectl top pods -n production

# Ver configuración aplicada
kubectl get deployment catalog -n production -o yaml
```

---

## 8. Respuestas Rápidas para Entrevista

### "¿Qué es un Namespace?"

```
Un namespace es una división lógica dentro del cluster de Kubernetes.
Sirve para organizar recursos, aislar ambientes, aplicar quotas y RBAC.
Por ejemplo, puedo tener namespaces para dev, staging, production y monitoring.
```

### "¿Diferencia entre Deployment y ReplicaSet?"

```
ReplicaSet garantiza que N réplicas estén corriendo, pero NO sabe hacer rolling updates.
Deployment es un wrapper sobre ReplicaSet que agrega rolling updates, rollbacks y versionado.
En la práctica, siempre usas Deployment. Nunca creas ReplicaSet directamente.
Cuando actualizas un Deployment, crea un nuevo ReplicaSet y migra los pods gradualmente.
```

### "¿Qué instalarías en EKS con Helm?"

```
1. AWS Load Balancer Controller — para que funcionen los Ingress
2. Prometheus + Grafana — para monitoring
3. Fluent Bit — para enviar logs a CloudWatch
4. Secrets Store CSI Driver — para montar secrets de AWS Secrets Manager
5. Cert Manager — para certificados TLS automáticos
6. External DNS — para actualizar Route53 automáticamente
7. Metrics Server — para kubectl top y HPA
```

### "¿Cómo harías una tarea programada en Kubernetes?"

```
Usaría un CronJob. Es como cron de Linux pero en Kubernetes.
Por ejemplo, para actualizar el catálogo cada 30 minutos:
schedule: "*/30 * * * *"
El CronJob crea un Job cada vez que se ejecuta, y el Job crea un Pod.
```

---

## Recursos Adicionales

- [Kubernetes Docs — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Docs — Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
- [Kubernetes Docs — CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Helm Charts](https://artifacthub.io/)

---

**Última actualización:** 2026-04-13

---

## 📖 Navegación

- **⬅️ Anterior:** [06-scripting-coding-prep.md](./06-scripting-coding-prep.md) — Scripting
- **➡️ Siguiente:** [08-git-submodules-workflow.md](./08-git-submodules-workflow.md) — Git Submodules
- **🏠 Inicio:** [README.md](./README.md) — Índice de documentación
- **🔝 Volver al inicio:** [00-concepts-overview.md](./00-concepts-overview.md) — Mapa de conceptos
