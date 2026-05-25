# 07 — Kubernetes Deep Dive

> Fundamental Kubernetes concepts you must master for EPAM DevOps/SRE technical interviews.

---

## 1. Deployment vs ReplicaSet

### What is a ReplicaSet?

```
ReplicaSet
├── Ensures N replicas of a pod are running
├── If a pod dies, it automatically creates another one
├── Uses a selector to identify which pods it manages
└── Does NOT know how to perform rolling updates
```

**ReplicaSet Example:**

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

**The Problem:** If you change the image to `catalog:v2` and run `kubectl apply`, the ReplicaSet will NOT update the existing pods. It will only create new pods with v2 if an existing pod dies.

---

### What is a Deployment?

```
Deployment (What YOU create)
├── It's a wrapper ON TOP OF the ReplicaSet
├── Adds: rolling updates, rollbacks, versioning
├── Maintains a history of ReplicaSets
└── Strategies: RollingUpdate, Recreate
```

**Hierarchy:**

```
Deployment: catalog-deployment
│
├── ReplicaSet: catalog-deployment-7d4f8c9b (v1) ← old, 0 replicas
│   ├── Pod: catalog-7d4f8c9b-abc12 (terminated)
│   ├── Pod: catalog-7d4f8c9b-def34 (terminated)
│   └── Pod: catalog-7d4f8c9b-ghi56 (terminated)
│
└── ReplicaSet: catalog-deployment-9f6a2e1d (v2) ← new, 3 replicas
    ├── Pod: catalog-9f6a2e1d-xyz78 (running)
    ├── Pod: catalog-9f6a2e1d-uvw90 (running)
    └── Pod: catalog-9f6a2e1d-rst12 (running)
```

**Deployment Example:**

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
      maxSurge: 1        # maximum 1 extra pod during update
      maxUnavailable: 0  # always maintain 3 available pods
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
        image: catalog:v2  # ← change this
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

### What happens when you update a Deployment?

```bash
# 1. Change the image in the YAML
kubectl set image deployment/catalog-deployment catalog=catalog:v2

# 2. Kubernetes handles this automatically:
```

```
Step 1: Deployment creates ReplicaSet-v2 with 0 replicas
Step 2: Scales up 1 pod in ReplicaSet-v2 (maxSurge: 1)
Step 3: Waits for the pod to be Ready (readinessProbe)
Step 4: Scales down 1 pod in ReplicaSet-v1
Step 5: Repeats until ReplicaSet-v2 has 3 replicas
Step 6: ReplicaSet-v1 remains with 0 replicas (but is NOT deleted)
```

**Rollback:**

```bash
# View history
kubectl rollout history deployment/catalog-deployment

# Revert to the previous version
kubectl rollout undo deployment/catalog-deployment

# Revert to a specific version
kubectl rollout undo deployment/catalog-deployment --to-revision=2
```

---

### Quick Comparison

| Feature | ReplicaSet | Deployment |
|----------------|------------|------------|
| Maintains N replicas | ✅ | ✅ |
| Self-healing (recreates pods) | ✅ | ✅ |
| Rolling updates | ❌ | ✅ |
| Rollback | ❌ | ✅ |
| Version History | ❌ | ✅ |
| Deployment Strategies | ❌ | ✅ |
| **When to use it** | Never directly | Always |

**Golden Rule:** ALWAYS use a Deployment. NEVER create a ReplicaSet directly.

---

## 2. Namespaces

### What is a Namespace?

```
A namespace is a logical division within a Kubernetes cluster.
It's like having "folders" to organize and isolate resources.
```

**Typical Structure:**

```
EKS Cluster: my-cluster
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
└── namespace: kube-system  ← K8s internal components
    ├── deployment/coredns
    ├── daemonset/kube-proxy
    └── deployment/aws-load-balancer-controller
```

---

### What are Namespaces for?

#### 1. Organization

```bash
# Group resources by team, environment, or application
kubectl get pods -n production
kubectl get pods -n dev
kubectl get pods -n monitoring
```

#### 2. Isolation

```yaml
# Network Policy: only pods in "production" can talk to each other
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
    - podSelector: {}  # only pods from the same namespace
```

#### 3. Resource Quotas

```yaml
# Limit CPU/memory per namespace
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

#### 4. RBAC (Access Control)

```yaml
# Grant permissions only to a specific namespace
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

#### 5. Name Conflict Prevention

```bash
# You can have a "catalog" deployment in dev AND production without conflict
kubectl get deployment catalog -n dev
kubectl get deployment catalog -n production
```

---

### Essential Commands

```bash
# List namespaces
kubectl get namespaces
kubectl get ns

# Create a namespace
kubectl create namespace staging

# View resources in a namespace
kubectl get pods -n production
kubectl get all -n production

# View resources in ALL namespaces
kubectl get pods --all-namespaces
kubectl get pods -A

# Change default namespace (to avoid typing -n every time)
kubectl config set-context --current --namespace=production

# Describe a namespace
kubectl describe namespace production

# Delete a namespace (BE CAREFUL: deletes EVERYTHING inside)
kubectl delete namespace dev
```

---

### DNS Between Namespaces

Services have automatic DNS records:

```
<service-name>.<namespace>.svc.cluster.local
```

**Example:**

```yaml
# Service in "production" namespace
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

**From another pod in the SAME namespace:**

```bash
curl http://catalog-svc:8080
```

**From another pod in a DIFFERENT namespace:**

```bash
curl http://catalog-svc.production.svc.cluster.local:8080
```

---

### Default Namespaces

Kubernetes creates these namespaces automatically:

| Namespace | Purpose |
|-----------|-----------|
| `default` | Default namespace if none is specified |
| `kube-system` | K8s internal components (DNS, proxy, etc.) |
| `kube-public` | Public resources, readable by everyone |
| `kube-node-lease` | Node heartbeats (to detect node failures) |

---

## 3. CronJob — Scheduled Tasks

### What is a CronJob?

```
CronJob = Linux cron + Kubernetes
Executes a Job at a specific time (like crontab)
```

**Use Case:** Synchronize catalog every 30 minutes

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: catalog-sync
  namespace: production
spec:
  schedule: "*/30 * * * *"  # every 30 minutes
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

**Schedule Syntax (same as cron):**

```
┌───────────── minute (0 - 59)
│ ┌───────────── hour (0 - 23)
│ │ ┌───────────── day of the month (1 - 31)
│ │ │ ┌───────────── month (1 - 12)
│ │ │ │ ┌───────────── day of the week (0 - 6) (Sunday=0)
│ │ │ │ │
* * * * *
```

**Examples:**

```bash
"0 2 * * *"       # Every day at 2:00 AM
"*/15 * * * *"    # Every 15 minutes
"0 */6 * * *"     # Every 6 hours
"0 9 * * 1"       # Mondays at 9:00 AM
"0 0 1 * *"       # First day of the month at midnight
```

**Commands:**

```bash
# View CronJobs
kubectl get cronjobs -n production

# View Jobs created by the CronJob
kubectl get jobs -n production

# View logs from the latest Job
kubectl logs -n production job/catalog-sync-28471234

# Execute manually (without waiting for the schedule)
kubectl create job --from=cronjob/catalog-sync manual-sync-1 -n production
```

---

## 4. Components Installed via Helm on EKS

### Full List for Interviews

```bash
# 1. AWS Load Balancer Controller (MANDATORY for Ingress)
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

# 5. Cert Manager (for automatic TLS via Let's Encrypt)
helm repo add jetstack https://charts.jetstack.io
helm install cert-manager jetstack/cert-manager \
  --namespace cert-manager --create-namespace \
  --set installCRDs=true

# 6. External DNS (automatically updates Route53)
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install external-dns bitnami/external-dns \
  --namespace kube-system \
  --set provider=aws \
  --set aws.region=us-east-1

# 7. Metrics Server (for kubectl top and HPA)
helm repo add metrics-server https://kubernetes-sigs.github.io/metrics-server/
helm install metrics-server metrics-server/metrics-server \
  --namespace kube-system

# 8. Ingress NGINX (ALB Controller alternative)
helm repo add ingress-nginx https://kubernetes.github.io/ingress-nginx
helm install ingress-nginx ingress-nginx/ingress-nginx \
  --namespace ingress-nginx --create-namespace
```

---

### Summary Table

| Component | Purpose | Typical Namespace |
|------------|----------------|------------------|
| AWS Load Balancer Controller | Creates ALB/NLB from Ingress | kube-system |
| Prometheus + Grafana | Metrics and Dashboards | monitoring |
| Fluent Bit | Ships logs to CloudWatch | kube-system |
| Secrets Store CSI Driver | Mounts secrets from AWS Secrets Manager | kube-system |
| Cert Manager | Automatic TLS Certificates | cert-manager |
| External DNS | Automatic Route53 updates | kube-system |
| Metrics Server | `kubectl top`, HPA | kube-system |
| Ingress NGINX | Alternative Ingress Controller | ingress-nginx |

---

## 5. Probes — Liveness vs Readiness

### Liveness Probe

```
Is the container alive?
If it fails → Kubernetes KILLS the pod and creates a new one
```

**When to use:** Detect deadlocks or hung processes.

```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8080
  initialDelaySeconds: 30  # wait 30s before starting checks
  periodSeconds: 10        # check every 10s
  timeoutSeconds: 5        # 5s timeout
  failureThreshold: 3      # 3 consecutive failures → kill pod
```

---

### Readiness Probe

```
Is the container ready to receive traffic?
If it fails → Kubernetes REMOVES the pod from the Service (no requests)
          → But it does NOT kill the pod
```

**When to use:** Wait for the app to initialize (DB connections, cache warmup).

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
Has the container finished starting up?
If it fails → Kubernetes KILLS the pod
Useful for apps that take a long time to boot.
```

```yaml
startupProbe:
  httpGet:
    path: /startup
    port: 8080
  initialDelaySeconds: 0
  periodSeconds: 10
  failureThreshold: 30  # 30 attempts × 10s = 5 minutes maximum
```

---

### Probe Types

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

# 3. Exec (command)
livenessProbe:
  exec:
    command:
    - cat
    - /tmp/healthy
```

---

## 6. Other Important Resources

### StatefulSet

```
For stateful applications (databases, queues)
- Pods have stable identities (catalog-0, catalog-1, catalog-2)
- Persistent volumes per pod
- Guaranteed order for deployment/scaling
```

**When to use:** PostgreSQL, Redis, Kafka, Elasticsearch.

---

### DaemonSet

```
Runs 1 pod on EVERY node in the cluster.
```

**When to use:** Logging agents, monitoring agents, network plugins.

---

### Job

```
Executes a task until completion (not a continuous service).
```

**When to use:** Database migrations, batch processing.

---

## 7. Essential Troubleshooting Commands

```bash
# View pods with more detail
kubectl get pods -o wide -n production

# Describe pod (events, status)
kubectl describe pod catalog-9f6a2e1d-xyz78 -n production

# Logs
kubectl logs catalog-9f6a2e1d-xyz78 -n production
kubectl logs -f catalog-9f6a2e1d-xyz78 -n production  # follow
kubectl logs --previous catalog-9f6a2e1d-xyz78        # logs from previous pod (if crashed)

# Execute command inside a pod
kubectl exec -it catalog-9f6a2e1d-xyz78 -n production -- /bin/bash
kubectl exec catalog-9f6a2e1d-xyz78 -n production -- curl localhost:8080/health

# View endpoints (which pods are behind a Service)
kubectl get endpoints catalog-svc -n production

# View cluster events
kubectl get events -n production --sort-by='.lastTimestamp'

# Port forward (for debugging)
kubectl port-forward pod/catalog-9f6a2e1d-xyz78 8080:8080 -n production

# View resource usage
kubectl top nodes
kubectl top pods -n production

# View applied configuration
kubectl get deployment catalog -n production -o yaml
```

---

## 8. Quick Interview Answers

### "What is a Namespace?"

```
A namespace is a logical division within a Kubernetes cluster. 
It serves to organize resources, isolate environments, apply quotas, and implement RBAC.
For example, I can have namespaces for dev, staging, production, and monitoring.
```

### "Difference between a Deployment and a ReplicaSet?"

```
A ReplicaSet ensures that N replicas are running but does NOT know how to perform rolling updates.
A Deployment is a wrapper around a ReplicaSet that adds rolling updates, rollbacks, and versioning.
In practice, you always use a Deployment; you never create a ReplicaSet directly.
When you update a Deployment, it creates a new ReplicaSet and gradually migrates pods.
```

### "What would you install on EKS using Helm?"

```
1. AWS Load Balancer Controller — to enable Ingress
2. Prometheus + Grafana — for monitoring
3. Fluent Bit — to ship logs to CloudWatch
4. Secrets Store CSI Driver — to mount secrets from AWS Secrets Manager
5. Cert Manager — for automatic TLS certificates
6. External DNS — for automatic Route53 updates
7. Metrics Server — for kubectl top and HPA
```

### "How would you handle a scheduled task in Kubernetes?"

```
I would use a CronJob. It's like Linux cron but within Kubernetes.
For example, to sync a catalog every 30 minutes: schedule: "*/30 * * * *"
The CronJob creates a Job each time it triggers, and that Job creates a Pod to execute the task.
```

---

## Additional Resources

- [Kubernetes Docs — Deployments](https://kubernetes.io/docs/concepts/workloads/controllers/deployment/)
- [Kubernetes Docs — Namespaces](https://kubernetes.io/docs/concepts/overview/working-with-objects/namespaces/)
- [Kubernetes Docs — CronJob](https://kubernetes.io/docs/concepts/workloads/controllers/cron-jobs/)
- [AWS EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)
- [Helm Charts](https://artifacthub.io/)

---

**Last updated:** 2026-05-13

---

## 📖 Navigation

- **⬅️ Previous:** [06-scripting-coding-prep.en.md](./06-scripting-coding-prep.en.md)
- **➡️ Next:** [08-git-submodules-workflow.en.md](./08-git-submodules-workflow.en.md)
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md)
