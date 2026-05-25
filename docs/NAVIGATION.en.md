# 🧭 Documentation Navigation

> Visual map of how all documents are interconnected.

---

## Sequential Flow

```
┌─────────────────────────────────────────────────────────────┐
│  00-concepts-overview.en.md                                 │
│  Concept Map — Read me first                                │
│  • The Big Picture                                          │
│  • Kubernetes from scratch                                  │
│  • Ingress, Helm, EKS, IRSA                                 │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  01-eks-ingress-alb.en.md                                   │
│  EKS + Ingress + ALB Controller                             │
│  • AWS Load Balancer Controller                             │
│  • Ingress Annotations                                      │
│  • Troubleshooting                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  02-terraform-basics.en.md                                  │
│  Terraform Fundamentals                                     │
│  • Providers, resources, variables                          │
│  • Lifecycle: init, plan, apply                             │
│  • Basic state management                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  03-terraform-concepts.en.md                                │
│  Advanced Terraform                                         │
│  • Remote state (S3 + DynamoDB)                             │
│  • Workspaces, for_each, dynamic blocks                     │
│  • Lifecycle rules                                          │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  04-cicd-concepts.en.md                                     │
│  CI/CD with GitLab, Jenkins, AWS                            │
│  • GitLab CI/CD: stages, jobs, variables                    │
│  • GitLab OIDC                                              │
│  • Deployment strategies                                     │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  05-observability-concepts.en.md                            │
│  Observability: Metrics, Logs, Traces                       │
│  • CloudWatch, Prometheus, Grafana                          │
│  • SLI/SLO dashboards                                       │
│  • Basic PromQL                                             │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  06-scripting-coding-prep.en.md                             │
│  Scripting & Coding Preparation                             │
│  • Python patterns (streaming, parsing, boto3)              │
│  • Bash one-liners (jq, awk, cut, sort)                     │
│  • System troubleshooting                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  07-kubernetes-deep-dive.en.md ⭐                            │
│  Kubernetes Deep Dive                                       │
│  • Deployment vs ReplicaSet                                 │
│  • Namespaces, CronJob, Probes                              │
│  • Helm components on EKS                                   │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│  08-git-submodules-workflow.en.md ⭐                         │
│  Git Submodules Management                                  │
│  • Why lab-11 is on GitLab                                  │
│  • How to clone and update submodules                       │
│  • Troubleshooting                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Document Navigation Header/Footer

Each document includes at the end:

```markdown
## 📖 Navigation

- **⬅️ Previous:** [previous-doc.en.md](./previous-doc.en.md)
- **➡️ Next:** [next-doc.en.md](./next-doc.en.md)
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md)
```

---

## Recommended Learning Paths

### 🎯 For Interview Preparation (Priority)

```
07-kubernetes-deep-dive.en.md (START HERE)
    ↓
04-cicd-concepts.en.md
    ↓
05-observability-concepts.en.md
    ↓
06-scripting-coding-prep.en.md
    ↓
03-terraform-concepts.en.md
```

### 🌱 For Beginners (From Scratch)

```
00-concepts-overview.en.md
    ↓
02-terraform-basics.en.md
    ↓
07-kubernetes-deep-dive.en.md
    ↓
01-eks-ingress-alb.en.md
    ↓
06-scripting-coding-prep.en.md
```

### 🔧 For Troubleshooting

```
07-kubernetes-deep-dive.en.md (Troubleshooting commands)
    ↓
01-eks-ingress-alb.en.md (Ingress issues)
    ↓
../troubleshooting/ (Real-world cases)
```

### 🛠️ For Repo Maintenance

```
08-git-submodules-workflow.en.md (Submodule management)
    ↓
../labs/lab-11-gitlab-oidc-mini/ (Lab on GitLab)
```

---

## Connections between Docs and Labs

### Observability (docs/05 ↔ labs)

```
docs/05-observability-concepts.en.md
    ↓
    ├─→ labs/lab-07-monitoring/
    │   └─→ Prometheus + Grafana on EKS
    │       • kube-prometheus-stack
    │       • PromQL queries
    │       • Golden signals dashboards
    │
    ├─→ labs/lab-09-cloudwatch-logs/
    │   └─→ CloudWatch Logs + Metric Filters
    │       • EC2 with log generator
    │       • CloudWatch Agent
    │       • Logs Insights queries
    │
    └─→ labs/scripting/
        └─→ Log analysis with Python
            • log_analyzer.py
            • SLO check
            • Large file streaming
```

---

| I need to... | Go to... |
|-------------|---------|
| Understand Deployment vs ReplicaSet | [07-kubernetes-deep-dive.en.md](./07-kubernetes-deep-dive.en.md#1-deployment-vs-replicaset) |
| Configure GitLab CI with OIDC | [04-cicd-concepts.en.md](./04-cicd-concepts.en.md) |
| Kubectl essential commands | [07-kubernetes-deep-dive.en.md](./07-kubernetes-deep-dive.en.md#7-essential-troubleshooting-commands) |
| Terraform Remote State | [03-terraform-concepts.en.md](./03-terraform-concepts.en.md) |
| Python Streaming patterns | [06-scripting-coding-prep.en.md](./06-scripting-coding-prep.en.md) |
| Work with lab-11 | [08-git-submodules-workflow.en.md](./08-git-submodules-workflow.en.md) |
| Ingress not generating ALB | [01-eks-ingress-alb.en.md](./01-eks-ingress-alb.en.md) |
| SLI/SLO dashboards | [05-observability-concepts.en.md](./05-observability-concepts.en.md) |
| **Prometheus + Grafana on EKS** | [../labs/lab-07-monitoring/Readme.md](../labs/lab-07-monitoring/Readme.md) |
| **CloudWatch Logs + Metric Filters** | [../labs/lab-09-cloudwatch-logs/Readme.md](../labs/lab-09-cloudwatch-logs/Readme.md) |
| **Scripting Exercises** | [../labs/scripting/README.md](../labs/scripting/README.md) |

---

## Full Repository Structure

```
epam-aws-devops-prep/
│
├── docs/                        ← YOU ARE HERE
│   ├── README.en.md             # English Index
│   ├── NAVIGATION.en.md         # This file
│   ├── 00-concepts-overview.en.md
│   ├── 01-eks-ingress-alb.en.md
│   ├── 02-terraform-basics.en.md
│   ├── 03-terraform-concepts.en.md
│   ├── 04-cicd-concepts.en.md
│   ├── 05-observability-concepts.en.md
│   ├── 06-scripting-coding-prep.en.md
│   ├── 07-kubernetes-deep-dive.en.md
│   └── 08-git-submodules-workflow.en.md
│
├── labs/                        # Hands-on Labs
│   ├── lab-01-vpc/
│   ├── lab-02-iam/
│   ├── ...
│   └── scripting/
│
└── troubleshooting/             # Real-world Incidents
    ├── 01-librechat-ingress.md
    ├── 02-jwt-dst-incident.md
    └── ...
```

---

**Last updated:** 2026-05-13
