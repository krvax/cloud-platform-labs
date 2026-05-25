# Understanding Ingress, ALB, and Target Groups in EKS

> 📚 Reference document for Kubernetes labs on AWS EKS.

---

## Table of Contents

- [General Analogy](#general-analogy)
- [Key Components](#key-components)
  - [Pod](#1-pod)
  - [Service](#2-service)
  - [Ingress](#3-ingress)
  - [Ingress Controller](#4-ingress-controller)
- [ALB and Target Groups](#alb-and-target-groups)
- [Full Flow](#full-flow)
- [Common Errors](#common-errors)
- [Diagnostic Commands](#diagnostic-commands)
- [References](#references)

---

## General Analogy

Imagine your EKS cluster is an **office building**:

```text
🌐 Internet (Users)
       │
       ▼
   🚪 INGRESS        ← Building Reception
       │                 (Decides which office to send you to)
       ▼
   🔀 SERVICE         ← Floor Directory
       │                 (Knows where each team is located)
       ▼
   📦 PODS            ← Working Offices
                         (Your running app)
```

---

## Key Components

### 1. 📦 Pod

The smallest unit in Kubernetes. Your container runs inside a Pod.

```yaml
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
    - name: my-app
      image: my-image:latest
      ports:
        - containerPort: 3080
```

> ⚠️ The Pod alone **is not accessible** from outside the cluster.

---

### 2. 🔀 Service

Exposes Pods internally within the cluster. Acts as an internal DNS.

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-service
spec:
  selector:
    app: my-app
  ports:
    - port: 80
      targetPort: 3080
  type: ClusterIP
```

**Service Types:**

| Type | Accessibility |
|------|--------------|
| `ClusterIP` | Internal cluster only |
| `NodePort` | Exposes a port on each node |
| `LoadBalancer` | Creates an external Load Balancer (expensive, one per service) |

> 💡 With `ClusterIP`, other internal services can communicate, but **it remains inaccessible from the internet**.

---

### 3. 🚪 Ingress

A Kubernetes resource that defines **routing rules** for external traffic toward internal Services.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-app-ingress
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /
spec:
  rules:
    - host: app.mydomain.com
      http:
        paths:
          - path: /
            pathType: Prefix
            backend:
              service:
                name: my-app-service
                port:
                  number: 80
```

**Important Annotations for AWS ALB:**

| Annotation | Description |
|-----------|-------------|
| `kubernetes.io/ingress.class: alb` | Use ALB as the ingress controller |
| `alb.ingress.kubernetes.io/scheme` | `internet-facing` or `internal` |
| `alb.ingress.kubernetes.io/target-type` | `ip` (direct to pod) or `instance` (to node) |
| `alb.ingress.kubernetes.io/healthcheck-path` | Path to verify pod health |
| `alb.ingress.kubernetes.io/certificate-arn` | SSL certificate ARN in ACM |

> ⚠️ The Ingress **only defines rules**. On its own, it does nothing. It requires an **Ingress Controller** to execute them.

---

### 4. 🎛️ Ingress Controller

The component that **reads Ingress rules** and creates the actual infrastructure.

On AWS EKS, we use the **AWS Load Balancer Controller**:

```text
Ingress YAML (Rules)
    │
    ▼
AWS Load Balancer Controller
    │
    ├──→ Creates an ALB in AWS
    ├──→ Creates Target Groups
    ├──→ Configures listeners and rules
    └──→ Registers Pods/IPs as targets
```

**Installation with Helm:**

```bash
helm repo add eks https://aws.github.io/eks-charts
helm repo update

helm install aws-load-balancer-controller eks/aws-load-balancer-controller \
  -n kube-system \
  --set clusterName=<CLUSTER_NAME> \
  --set serviceAccount.create=false \
  --set serviceAccount.name=aws-load-balancer-controller

# Verify
kubectl get deployment -n kube-system aws-load-balancer-controller
```

> 🔑 **Prerequisite:** The controller needs an IAM Role with permissions to create ALBs, Target Groups, etc.

---

## ALB and Target Groups

### What is the ALB?

**Application Load Balancer** — AWS Layer 7 Load Balancer.

```text
🌐 User → app.mydomain.com
        │
        ▼
┌──────────────────┐
│       ALB        │
│  (Layer 7 - HTTP)│
│                  │
│  Listeners:      │
│  :80  → Rules    │
│  :443 → Rules    │
└────────┬─────────┘
          │
          ▼
    Target Groups
```

**Features:**
- Operates at **Layer 7** (HTTP/HTTPS)
- Understands URLs, headers, paths
- Path-based routing: `/api` → backend, `/` → frontend
- Supports SSL/TLS termination
- Created **automatically** by AWS LB Controller

### What is a Target Group?

It's the **list of destinations** where the ALB sends traffic.

```text
┌────────────────────────┐
│     Target Group       │
│                        │
│  Pod 1: ✅ healthy     │  ← Receives traffic
│  Pod 2: ✅ healthy     │  ← Receives traffic
│  Pod 3: ❌ unhealthy   │  ← NO traffic received
│                        │
│  Health Check:         │
│  GET / → 200 OK       │
└────────────────────────┘
```

---

## Full Flow

```text
helm install my-app ./chart
        │
        ├── Creates Deployment → Pods (app running)
        ├── Creates Service (exposes pods internally)
        └── Creates Ingress (routing rules)
                │
                ▼
    AWS LB Controller (detects Ingress)
                │
                ├── Creates ALB in AWS
                ├── Creates Target Group
                ├── Registers Pod IPs as targets
                └── Configures health checks
                        │
                        ▼
    ✅ app.mydomain.com → ALB → Target Group → Pod → App
```

---

## Common Errors

### ❌ Error 1: ALB Controller not installed

**Symptom:** Ingress does not get an ADDRESS.

```bash
kubectl get ingress
# NAME              HOSTS   ADDRESS   PORTS   AGE
# my-app-ingress    *                 80      5m
#                           ^^^^^^^^ EMPTY = problem
```

**Solution:** Install the AWS Load Balancer Controller.

---

### ❌ Error 2: Unhealthy Targets

**Symptom:** ALB returns 502 Bad Gateway.

**Common Causes:**
- Pod is crashing (missing env vars, secrets)
- Incorrect `healthcheck-path`
- `targetPort` doesn't match container port
- Security Groups blocking traffic

---

### ❌ Error 3: Missing IAM Permissions

**Symptom:** Controller cannot create resources in AWS.

```bash
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller
# "AccessDenied: User is not authorized..."
```

**Solution:** Verify IAM Role of the ServiceAccount.

---

### ❌ Error 4: Incorrect Annotations

```yaml
# ✅ Minimum necessary annotations
metadata:
  annotations:
    kubernetes.io/ingress.class: alb
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
    alb.ingress.kubernetes.io/healthcheck-path: /
```

---

## Diagnostic Commands

```bash
# === INGRESS ===
kubectl get ingress
kubectl describe ingress <name>

# === PODS ===
kubectl get pods
kubectl logs <pod-name>
kubectl describe pod <pod-name>

# === ALB CONTROLLER ===
kubectl get pods -n kube-system | grep load-balancer
kubectl logs -n kube-system -l app.kubernetes.io/name=aws-load-balancer-controller

# === AWS CLI ===
aws elbv2 describe-load-balancers
aws elbv2 describe-target-groups
aws elbv2 describe-target-health --target-group-arn <arn>
```

---

## References

- [AWS Load Balancer Controller](https://kubernetes-sigs.github.io/aws-load-balancer-controller)
- [Kubernetes Ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/)
- [AWS ALB Docs](https://docs.aws.amazon.com/elasticloadbalancing/latest/application/)
- [EKS Best Practices](https://aws.github.io/aws-eks-best-practices/)

---

> 🏷️ Tags: `kubernetes` `eks` `ingress` `alb` `aws` `networking`

---

## 📖 Navigation

- **⬅️ Previous:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
- **➡️ Next:** [02-terraform-basics.en.md](./02-terraform-basics.en.md) — Terraform Fundamentals
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
