# Exercise 04: Prometheus + Grafana (Proxy Observability)

> Prerequisite: Exercise 01 + 03 completed (envoy-proxy running in proxy-lab namespace)
> Tools: Helm, Prometheus, Grafana

---

## Objective

Add observability to the Envoy proxy:
- **Prometheus** scrapes metrics from Envoy's admin endpoint
- **Grafana** visualizes them in dashboards
- Demonstrates the monitoring stack you'd use in production

---

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│  Namespace: proxy-lab                                   │
│                                                         │
│  ┌──────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │ httpbin  │◄───│ envoy-proxy  │    │  Prometheus  │  │
│  │          │    │  :8080 proxy │◄───│  (scrapes    │  │
│  └──────────┘    │  :9901 admin │    │   :9901)     │  │
│                  └──────────────┘    └──────┬───────┘  │
│  ┌──────────┐                               │          │
│  │  nginx   │                        ┌──────▼───────┐  │
│  │          │                        │   Grafana    │  │
│  └──────────┘                        │  (dashboards)│  │
│                                      └──────────────┘  │
└─────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Helm Chart vs Blueprint

| Concept | What it is | Analogy |
|---------|-----------|---------|
| **Helm Chart** | Package of K8s manifests with templates + values.yaml | Cookbook recipe with adjustable ingredients |
| **Blueprint** | Generic term for reusable infra design/pattern | Architectural floor plan |

Helm is K8s-specific. Blueprint is a concept (could be Terraform modules, CloudFormation, etc.)

### Where would you install Prometheus in production?

| Method | How | When |
|--------|-----|------|
| Helm CLI | `helm install ...` | Labs, prototypes (what we do here) |
| Terraform + Helm provider | `resource "helm_release"` | Enterprise IaC (everything in code) |
| ArgoCD (GitOps) | Application CRD points to chart | Production with GitOps |
| Helmfile | Declarative multi-chart | Many charts to manage together |

**Interview answer:**
> "In labs I use Helm CLI. In production I prefer Terraform helm_release for IaC, or ArgoCD for GitOps — desired state in Git, auto-reconciled."

### What Prometheus does

- **Scrapes** metrics from endpoints at regular intervals (pull model)
- **Stores** time-series data (TSDB)
- **Queries** via PromQL
- Does NOT visualize — that's Grafana's job

### What Grafana does

- **Visualizes** data from Prometheus (and other sources)
- **Dashboards** with panels, graphs, alerts
- **Does NOT collect** data — it queries Prometheus

---

## Steps

### Step 1: Add Helm repos

```bash
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update
```

### Step 2: Install Prometheus (minimal, for minikube)

```bash
helm install prometheus prometheus-community/prometheus \
  --namespace proxy-lab \
  --set server.service.type=ClusterIP \
  --set alertmanager.enabled=false \
  --set kube-state-metrics.enabled=false \
  --set prometheus-node-exporter.enabled=false \
  --set prometheus-pushgateway.enabled=false \
  --set server.persistentVolume.enabled=false
```

**What the flags do:**
| Flag | Why |
|------|-----|
| `--namespace proxy-lab` | Install in same namespace as our proxy |
| `server.service.type=ClusterIP` | Internal only (no LoadBalancer needed in minikube) |
| `alertmanager.enabled=false` | Don't need alerting for this lab |
| `kube-state-metrics.enabled=false` | Reduces resource usage |
| `prometheus-node-exporter.enabled=false` | Don't need node metrics |
| `prometheus-pushgateway.enabled=false` | Don't need push gateway |
| `server.persistentVolume.enabled=false` | Uses emptyDir instead of PVC (lab only) |

### ⚠️ RCA: Why `persistentVolume.enabled=false`?

We hit two issues getting Prometheus to run:

**Issue 1: CrashLoopBackOff — `permission denied` on `/data`**
- Prometheus runs as user `nobody` (65534) for security
- The PVC volume didn't have correct permissions for that user
- Fix attempt: `runAsUser=0` (root)

**Issue 2: `CreateContainerConfigError` — `breaks non-root policy`**
- Minikube has Pod Security Admission that blocks root containers
- This is a good security practice (enforced in production too)

**Final fix: Disable PVC entirely**
- `emptyDir` = K8s creates a temp directory with correct permissions
- Data is lost if pod dies (acceptable for lab, NOT for production)

### What you'd do in production (interview answer)

**Option A: PVC with correct fsGroup (most common)**
```yaml
# values.yaml for helm
server:
  persistentVolume:
    enabled: true
    size: 50Gi
    storageClass: "gp3"  # AWS EBS gp3
  securityContext:
    runAsUser: 65534
    runAsGroup: 65534
    fsGroup: 65534       # This makes K8s chown the volume to this group
```

**Option B: Init container that fixes permissions**
```yaml
server:
  extraInitContainers:
    - name: fix-permissions
      image: busybox
      command: ['sh', '-c', 'chown -R 65534:65534 /data']
      volumeMounts:
        - name: storage-volume
          mountPath: /data
```

**Option C: Use kube-prometheus-stack (Prometheus Operator)**
```bash
helm install monitoring prometheus-community/kube-prometheus-stack
```
This handles everything automatically (PVCs, permissions, Grafana, alerting).

**Interview answer:**
> "In production I'd use kube-prometheus-stack which handles storage and permissions via the Prometheus Operator. For custom installs, I set fsGroup in the securityContext so K8s assigns correct ownership to the PVC automatically."

### Step 3: Configure Prometheus to scrape Envoy

Create `prometheus-scrape-config.yaml` — tells Prometheus where to find Envoy metrics.

### Step 4: Install Grafana

```bash
helm install grafana grafana/grafana \
  --namespace proxy-lab \
  --set adminPassword=admin123 \
  --set service.type=NodePort
```

### Step 5: Access Grafana

```bash
# Get the NodePort
minikube service grafana -n proxy-lab --url
```

### Step 6: Add Prometheus as data source in Grafana

- URL: `http://prometheus-server:80`
- Create dashboard with Envoy metrics

---

## Envoy metrics available at :9901/stats/prometheus

Key metrics to look for:
- `envoy_http_downstream_rq_total` — total requests
- `envoy_http_downstream_rq_xx` — requests by status code (2xx, 4xx, 5xx)
- `envoy_cluster_upstream_rq_time` — upstream latency
- `envoy_cluster_upstream_cx_active` — active connections

---

## Interview talking points

1. **"How do you monitor infrastructure?"**
   > "Prometheus for metrics collection (pull model), Grafana for visualization. In production I also use Datadog/New Relic for APM and distributed tracing."

2. **"What's the difference between pull and push monitoring?"**
   > "Prometheus pulls (scrapes endpoints). Push model (like StatsD) has services send metrics to a collector. Pull is better for service discovery in K8s."

3. **"How would you alert on proxy issues?"**
   > "Set up Prometheus alerting rules on error rate (5xx > threshold), latency p99, and connection count. Route alerts via Alertmanager to PagerDuty/Slack."
