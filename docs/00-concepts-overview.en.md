# 00 — Concept Map: Read Me First

> This document is your entry point before touching labs or checklists.
> If something about Kubernetes, EKS, Helm, or Karpenter sounds confusing, start here.

---

## Index

1. [The Big Picture: How everything fits together](#1-the-big-picture)
2. [Kubernetes from Scratch (No lies)](#2-kubernetes-from-scratch)
3. [Ingress: The Smart Gateway](#3-ingress-the-smart-gateway)
4. [Annotations: Messages Between Components](#4-annotations-messages-between-components)
5. [Helm: The K8s Package Manager](#5-helm-the-k8s-package-manager)
6. [EKS: Kubernetes on AWS](#6-eks-kubernetes-on-aws)
7. [IRSA: AWS Permissions for Pods (Without Access Keys)](#7-irsa-aws-permissions-for-pods)
8. [Karpenter: The Modern Autoscaler](#8-karpenter-the-modern-autoscaler)
9. [EKS Blueprints: Preconfigured Everything](#9-eks-blueprints-preconfigured-everything)
10. [Full HTTP Request Flow](#10-full-http-request-flow)
11. [Interview Questions with Answer Key](#11-interview-questions)

---

## 1. The Big Picture

Before diving into details, visualize the layers:

```
User
  │
  ▼
Internet / DNS (Route53)
  │
  ▼
AWS Load Balancer (ALB)          ← Automatically created by AWS LB Controller
  │
  ▼
Ingress (K8s Object)             ← Defines HTTP routing rules
  │
  ├─ /api   → Service "backend"
  └─ /app   → Service "frontend"
                │
                ▼
            Pods (The actual containers)
                │
                ▼
            AWS (S3, RDS, Secrets Manager...)  ← Accessed via IRSA, no access keys
```

**EKS** is the Kubernetes control plane running on AWS.
**Karpenter** decides how many nodes (EC2) exist to run those pods.
**Helm** is how you install all of this without writing 500 lines of YAML by hand.
**Terraform** is how you created the cluster and its components from code.

---

## 2. Kubernetes from Scratch

### Object Hierarchy (Smallest to Largest)

```
Pod
 └─ Deployment (Manages Pod replicas)
      └─ Service (Provides a stable IP for the Deployment)
           └─ Ingress (Routes HTTP to Services)
```

### Pod

The smallest unit. One or more containers sharing network and storage.
In practice, you almost never create Pods directly — you create Deployments.

```yaml
# Don't do this in production, just for understanding:
apiVersion: v1
kind: Pod
metadata:
  name: my-app
spec:
  containers:
    - name: app
      image: nginx:1.25
```

### Deployment

States: *"I want 3 replicas of this Pod, always"*. If a Pod dies, the Deployment creates another.
It also handles rolling updates: replaces pods one by one without downtime.

```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: my-app
spec:
  replicas: 3
  selector:
    matchLabels:
      app: my-app
  template:
    metadata:
      labels:
        app: my-app
    spec:
      containers:
        - name: app
          image: nginx:1.25
          resources:
            requests:
              cpu: "100m"
              memory: "128Mi"
            limits:
              cpu: "500m"
              memory: "256Mi"
```

> ⚠️ **Always define `requests` and `limits`**. Without them, a pod can consume all node resources and kill others (OOMKilled).

### Service

Pods have IPs that change every time they die and are reborn.
The Service provides a fixed IP (ClusterIP) that always points to the correct pods using **label selectors**.

| Type | Purpose |
|------|----------|
| `ClusterIP` | Internal traffic within the cluster |
| `NodePort` | Exposes a port on every node (for testing) |
| `LoadBalancer` | Automatically creates an ALB/NLB in AWS |

```yaml
apiVersion: v1
kind: Service
metadata:
  name: my-app-svc
spec:
  selector:
    app: my-app        # Points to pods with this label
  ports:
    - port: 80
      targetPort: 8080
  type: ClusterIP
```

### StatefulSet vs. Deployment

| | Deployment | StatefulSet |
|--|------------|-------------|
| Interchangeable Pods | ✅ Yes | ❌ No, each has an identity |
| Pod Naming | Random | Ordered (pod-0, pod-1...) |
| Shared Storage | Not necessarily | Dedicated PVC per pod |
| Typical Use | APIs, web apps | Databases, Redis, Kafka |

### DaemonSet

Runs **exactly one pod per node**. Useful for monitoring agents (Datadog, Fluentd) or CNI plugins.

### Job / CronJob

- **Job**: Runs a task until it completes successfully (e.g., DB migration).
- **CronJob**: A Job that repeats on a cron-style schedule.

---

## 3. Ingress: The Smart Gateway

### The problem it solves

Without Ingress, to expose 3 apps you need 3 AWS Load Balancers → expensive.
With Ingress, you have **1 ALB** that routes based on path or domain.

```
Without Ingress:                 With Ingress:
ALB-1 → app-frontend            ALB-1 → /app    → app-frontend
ALB-2 → app-backend                    /api    → app-backend
ALB-3 → app-admin                      /admin  → app-admin
```

### How it works (Two pieces)

1. **Ingress Controller**: A pod running in the cluster that listens for Ingress object changes and configures the actual ALB in AWS. In EKS, we use the **AWS Load Balancer Controller**.

2. **Ingress object**: The YAML you write declaring the routing rules.

```yaml
apiVersion: networking.k8s.io/v1
kind: Ingress
metadata:
  name: my-ingress
  annotations:
    kubernetes.io/ingress.class: alb              # Uses AWS LB Controller
    alb.ingress.kubernetes.io/scheme: internet-facing
    alb.ingress.kubernetes.io/target-type: ip
spec:
  rules:
    - host: api.mycompany.com
      http:
        paths:
          - path: /api
            pathType: Prefix
            backend:
              service:
                name: backend-svc
                port:
                  number: 80
          - path: /
            pathType: Prefix
            backend:
              service:
                name: frontend-svc
                port:
                  number: 80
```

> 💡 The AWS LB Controller sees this YAML → creates an ALB in AWS → configures listener rules with exactly those routes. It is completely automatic.

---

## 4. Annotations: Messages Between Components

Annotations are **metadata in key-value form** that external controllers read to know how to configure themselves.

Don't memorize them all. Understand the pattern:

```
<controller-prefix>/<name>: <value>
```

Real-world examples:

```yaml
annotations:
  # Tells AWS LB Controller to make the ALB public
  alb.ingress.kubernetes.io/scheme: internet-facing

  # Tells it to use an ACM certificate (HTTPS)
  alb.ingress.kubernetes.io/certificate-arn: arn:aws:acm:us-east-1:...

  # Tells cluster-autoscaler not to remove this node
  cluster-autoscaler.kubernetes.io/safe-to-evict: "false"

  # Tells Prometheus how to scrape metrics
  prometheus.io/scrape: "true"
  prometheus.io/port: "8080"
```

**Mental Rule**: When you see an annotation, ask yourself: *Which controller is going to read it?* That controller gives it meaning.

---

## 5. Helm: The K8s Package Manager

### The Analogy

Helm is like `apt` or `brew` for Kubernetes.
A **chart** is the package. It contains all the necessary YAMLs with **variables** (values).

```
Without Helm: Write 15 YAML files by hand to install Prometheus
With Helm: helm install prometheus prometheus-community/kube-prometheus-stack
```

### Essential Commands

```bash
# Add chart repository
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo update

# List charts in a repo
helm search repo prometheus-community

# View configurable values of a chart
helm show values prometheus-community/kube-prometheus-stack

# Install with custom values
helm install my-release prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --create-namespace \
  --set grafana.adminPassword=secret \
  --values my-values.yaml

# List installed releases
helm list -A

# Upgrade a release
helm upgrade my-release prometheus-community/kube-prometheus-stack

# Uninstall
helm uninstall my-release -n monitoring
```

### values.yaml: Customizing a Chart

```yaml
# my-values.yaml — only override what you need to change
grafana:
  adminPassword: "my-secure-password"
  service:
    type: LoadBalancer

prometheus:
  prometheusSpec:
    retention: 30d
    storageSpec:
      volumeClaimTemplate:
        spec:
          storageClassName: gp3
          resources:
            requests:
              storage: 50Gi
```

### Chart Structure (If asked)

```
my-chart/
  Chart.yaml          # Metadata (name, version, description)
  values.yaml         # Default values
  templates/          # YAMLs with placeholders {{ .Values.xxx }}
    deployment.yaml
    service.yaml
    ingress.yaml
    _helpers.tpl      # Reusable functions
```

---

## 6. EKS: Kubernetes on AWS

### What AWS manages vs. What you manage

| AWS Manages | You Manage |
|---|---|
| Control plane (API server, etcd, scheduler) | Node groups (EC2) |
| Control plane HA (automatic multi-AZ) | Networking (VPC CNI) |
| Control plane upgrades | Add-ons (CoreDNS, kube-proxy) |
| | Workloads (Your apps) |

### Compute Types in EKS

| Type | What it is | When to use it |
|---|---|---|
| Managed Node Groups | AWS-managed EC2 | Most cases |
| Self-managed nodes | EC2 you control | Very specific configurations |
| Fargate | Serverless, no nodes | Variable workloads, no node management |
| Karpenter | Karpenter-managed EC2 | Efficient and fast scaling |

### Critical EKS Add-ons

```bash
# View installed add-ons in your cluster
aws eks list-addons --cluster-name my-cluster

# Common add-ons:
# - vpc-cni          → Pod networking (VPC IPs)
# - coredns          → Internal cluster DNS
# - kube-proxy       → Service networking
# - aws-ebs-csi-driver → Storage (PVCs with EBS)
# - amazon-cloudwatch-observability → Metrics and logs
```

### kubeconfig: Connecting to the Cluster

```bash
# Configure kubectl to point to your EKS cluster
aws eks update-kubeconfig \
  --name my-cluster \
  --region us-east-1

# Verify
kubectl cluster-info
kubectl get nodes
```

---

## 7. IRSA: AWS Permissions for Pods

### The Problem

Your pods need to access S3, Secrets Manager, DynamoDB, etc.
Incorrect solution: Place access keys in environment variables or code.
Correct solution: **IRSA** (IAM Roles for Service Accounts).

### How it works (Simplified)

```
Pod → Uses ServiceAccount → ServiceAccount has annotation with IAM Role ARN
                                   ↓
                         AWS STS verifies pod's OIDC token
                                   ↓
                         AWS delivers temporary credentials to the pod
                                   ↓
                         Pod accesses S3/DynamoDB/etc. with those credentials
```

There are never any hardcoded access keys. Credentials are temporary and rotated automatically.

### Step-by-Step Setup

```bash
# 1. Associate OIDC provider with cluster (once)
eksctl utils associate-iam-oidc-provider \
  --cluster my-cluster \
  --approve

# 2. Create IAM Role + ServiceAccount
eksctl create iamserviceaccount \
  --name my-app-sa \
  --namespace production \
  --cluster my-cluster \
  --attach-policy-arn arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess \
  --approve

# 3. Reference the ServiceAccount in your Deployment
```

```yaml
spec:
  serviceAccountName: my-app-sa   # ← That's all you need in the pod
  containers:
    - name: app
      image: my-app:latest
      # No AWS_ACCESS_KEY_ID variables here
```

---

## 8. Karpenter: The Modern Autoscaler

### The problem it solves

The classic **Cluster Autoscaler** is slow and rigid: it works with pre-defined Node Groups and takes 3-5 minutes to add a node.

**Karpenter** is smarter:
- Monitors `Pending` pods and the resources they need.
- Chooses the optimal EC2 type for those pods (exact size, spot vs. on-demand).
- Provisions the node in ~30-60 seconds.
- Consolidates nodes when usage is low (bin packing).

### Key Concepts

**NodePool** (formerly Provisioner): Defines rules for nodes Karpenter can create.

```yaml
apiVersion: karpenter.sh/v1beta1
kind: NodePool
metadata:
  name: default
spec:
  template:
    spec:
      requirements:
        - key: karpenter.sh/capacity-type
          operator: In
          values: ["spot", "on-demand"]    # Prefers spot, falls back to on-demand
        - key: node.kubernetes.io/instance-type
          operator: In
          values: ["t3.medium", "t3.large", "m5.large"]
      nodeClassRef:
        name: default
  limits:
    cpu: 1000                              # Total cluster limit
  disruption:
    consolidationPolicy: WhenUnderutilized
    consolidateAfter: 30s
```

**EC2NodeClass**: AWS-specific configuration (AMI, subnets, security groups).

```yaml
apiVersion: karpenter.k8s.aws/v1beta1
kind: EC2NodeClass
metadata:
  name: default
spec:
  amiFamily: AL2
  role: "KarpenterNodeRole-my-cluster"
  subnetSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
  securityGroupSelectorTerms:
    - tags:
        karpenter.sh/discovery: my-cluster
```

### Karpenter vs. Cluster Autoscaler

| | Cluster Autoscaler | Karpenter |
|--|---|---|
| Speed | ~3-5 min | ~30-60 sec |
| Instance Selection | Fixed per Node Group | Dynamic, chooses optimal |
| Consolidation | Limited | Aggressive (bin packing) |
| Configuration | Node Groups in AWS | NodePool + EC2NodeClass in K8s |
| Spot Handling | Manual per Node Group | Automatic with fallback |

---

## 9. EKS Blueprints: Preconfigured Everything

### What it is

EKS Blueprints is a set of **Terraform modules** (or CDK) that creates a production-ready EKS cluster with all add-ons preconfigured.

Instead of:
1. Creating VPC with Terraform
2. Creating EKS cluster
3. Installing AWS LB Controller with Helm
4. Configuring IRSA for LB Controller
5. Installing Karpenter
6. ... (20+ more steps)

With Blueprints:

```hcl
module "eks_blueprints" {
  source = "github.com/aws-ia/terraform-aws-eks-blueprints"

  cluster_name    = "my-cluster"
  cluster_version = "1.29"
  vpc_id          = module.vpc.vpc_id
  private_subnet_ids = module.vpc.private_subnets

  # Add-ons with a flag
  enable_aws_load_balancer_controller = true
  enable_karpenter                    = true
  enable_metrics_server               = true
  enable_external_secrets             = true
}
```

**For the interview**: EKS Blueprints is not magic; it's automated Terraform + Helm + IRSA. If asked, describe the components it installs rather than treating it as a black box.

---

## 10. Full HTTP Request Flow

Tracing this flow from memory is a favorite interviewer question.

```
1. User types: https://api.mycompany.com/users

2. DNS (Route53) resolves api.mycompany.com → AWS ALB IP

3. ALB receives request on port 443
   └─ Terminates TLS with ACM certificate
   └─ Finds listener rule matching /users

4. ALB forwards to Target Group (cluster pods)
   └─ "ip" target type sends directly to Pod IP (not the node)

5. Request reaches app pod
   └─ Pod processes request
   └─ If DB needed: calls RDS in private subnet
   └─ If secrets needed: calls Secrets Manager via IRSA

6. Response returns via same path: Pod → ALB → User
```

**K8s Components Involved**:
- `Ingress` → Defined rule `/users → backend-svc`
- `Service (backend-svc)` → Selected the correct pods
- `AWS LB Controller` → Automatically created and configured the ALB
- `IRSA` → Allowed pod access to Secrets Manager without access keys

---

## 11. Interview Questions

### K8s Fundamentals

**"What happens when you run `kubectl apply -f deployment.yaml`?"**

```
1. kubectl sends YAML to API Server (HTTPS)
2. API Server authenticates (your kubeconfig) and authorizes (RBAC)
3. API Server validates object and stores in etcd
4. Deployment Controller detects change in etcd
5. Creates a ReplicaSet with the specifications
6. ReplicaSet creates Pods
7. Scheduler assigns each Pod to an available node
8. Node's kubelet downloads image and starts the container
```

---

**"A pod has been in `Pending` for 10 minutes. How do you diagnose it?"**

```bash
# Step 1: Check error events
kubectl describe pod <name> | grep -A20 Events

# Most common causes:
# - "Insufficient cpu/memory" → No node has enough resources
#   → Solution: Review pod requests, add nodes, or lower requests

# - "no nodes available to schedule" → All nodes have taints without toleration
#   → kubectl describe nodes | grep Taint

# - "0/3 nodes are available: persistentvolumeclaim not bound"
#   → kubectl get pvc → See if PVC is also Pending
#   → kubectl describe pvc → See why storage wasn't provisioned

# Step 2: Verify cluster resources
kubectl top nodes
kubectl describe nodes | grep -A5 "Allocated resources"
```

---

**"What is the difference between Deployment and StatefulSet?"**

```
Deployment:
- Pods are identical and interchangeable
- If a pod dies, replacement can go to any node
- Shared storage or no persistent storage
- E.g., REST API, web server

StatefulSet:
- Each pod has a unique identity (pod-0, pod-1, pod-2)
- Created and destroyed in order
- Each pod has its own PVC (independent storage)
- pod-0 is always the same pod (same name, same storage)
- E.g., PostgreSQL, Redis cluster, Kafka, Elasticsearch
```

---

**"What is a PodDisruptionBudget?"**

```
Defines how many pods can be unavailable during a voluntary disruption
(node upgrade, drain, etc.).

Example: I have 5 replicas, I want at least 4 available always:

apiVersion: policy/v1
kind: PodDisruptionBudget
spec:
  minAvailable: 4
  selector:
    matchLabels:
      app: my-app

Without PDB: A kubectl drain could kill all pods on a node at once.
With PDB: Kubernetes waits for another pod to be Ready before taking out the next.
```

---

### EKS / AWS

**"What is IRSA and why is it better than access keys in pods?"**

```
IRSA = IAM Roles for Service Accounts.

Problem with access keys:
- Hardcoded in env vars or code → leakage risk
- No automatic rotation
- If pod is compromised, attacker has indefinite access

IRSA Solution:
- Temporary credentials (expire in hours)
- Automatic rotation via AWS STS
- Least privilege principle (each ServiceAccount has its own role)
- If pod is compromised, credentials expire on their own
- Clear auditing in CloudTrail: which pod assumed which role
```

---

**"How does autoscaling work in EKS?"**

```
There are two independent types of autoscaling:

1. HPA (Horizontal Pod Autoscaler) — Scales Pods
   - Measures CPU/memory (or custom metrics)
   - Adds or removes Deployment replicas
   - Acts in seconds

2. Karpenter (or Cluster Autoscaler) — Scales Nodes
   - Detects Pending pods due to lack of resources
   - Adds EC2 nodes so those pods have somewhere to run
   - Acts in minutes (CA) or ~60 seconds (Karpenter)

Typical Flow:
Traffic spikes → HPA adds pods → Pods become Pending (no node)
→ Karpenter detects Pending → Creates EC2 → Pods are scheduled → Stable system
```

---

**"What would you do if a new deployment is causing production errors?"**

```bash
# Option 1: Immediate rollback
kubectl rollout undo deployment/my-app

# Verify rollback progress
kubectl rollout status deployment/my-app

# View version history
kubectl rollout history deployment/my-app

# Option 2: If using GitOps (ArgoCD)
# Revert commit in Git → ArgoCD detects change → Automatic rollback

# AFTER rollback: Investigate what failed
kubectl logs deployment/my-app --previous
kubectl describe deployment/my-app
# Review metrics in CloudWatch / Datadog for error period
```

---

### Incident Management (STAR Response)

**"Production is down. Users cannot log in. What do you do?"**

```
Structure: Detect → Mitigate → Investigate → Communicate → Post-mortem

1. DETECT
   - Confirm incident: Real or false positive?
   - kubectl get pods -n production (any pods down?)
   - Review dashboards: error rate, latency, saturation

2. MITIGATE (First, before investigating)
   - Was the last deploy recent? → kubectl rollout undo deployment/auth
   - Capacity issue? → kubectl scale deployment/auth --replicas=5
   - Goal is to restore service, not find root cause yet.

3. INVESTIGATE
   - kubectl logs deployment/auth --previous
   - kubectl describe pods -n production
   - Check CloudTrail: Recent IAM changes?
   - Check RDS: Saturated connections? Replication lag?

4. COMMUNICATE
   - Update status page every 15-20 minutes
   - Notify stakeholders: "Investigating, resolution ETA: X"

5. POST-MORTEM
   - Blameless, within 48h of incident
   - 5 Whys to reach root cause
   - Action items with owner and due date
```

---

> 💡 **Interview Tip**: If you don't know something, use this phrase:
> *"I haven't used that specific tool in production, but I'm familiar with the concept. In my experience I've solved a similar problem with X, which works by..."*
> This demonstrates honesty + learning ability + that you don't freeze up.

---

## 📖 Navigation

- **➡️ Next:** [01-eks-ingress-alb.en.md](./01-eks-ingress-alb.en.md) — EKS + Ingress + ALB
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
