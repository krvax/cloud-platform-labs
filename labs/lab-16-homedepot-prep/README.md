# Lab 16: Platform Operations — Proxy, IaC & Observability

> Prep for: Home Depot SRE (Vantage Proxy)
> Focus: Terraform, Ansible, Envoy/proxy, Grafana, Python scripting
> Runtime: Minikube (local K8s)

## Exercises

| # | Topic | Description | Status |
|---|-------|-------------|--------|
| 01 | Terraform + K8s | Deploy an Envoy proxy to K8s using Terraform (modules, variables, tfvars) | ✅ Done |
| 02 | Ansible Templates | Generate proxy config from Jinja2 templates with inventory | 🔲 |
| 03 | Envoy L7 Routing | Path-based routing: /api→httpbin, /→nginx. ConfigMap + rollout restart | ✅ Done |
| 04 | Prometheus + Grafana | Monitoring Envoy metrics (upstream_rq_total, latency, errors) | ✅ Done |
| 05 | Python Automation | Health check script, log parser, deployment validator | 🔲 |
| 06 | GitHub Actions (local) | CI/CD pipeline: `terraform fmt → validate → plan` using `act` | 🔲 |
| 07 | Jenkins + Shared Libraries | Jenkins in K8s + pipeline + Prometheus metrics + DORA dashboard | ✅ Done |

## RCAs

| # | Issue | Resolution | Link |
|---|-------|-----------|------|
| 001 | Envoy CrashLoopBackOff — invalid `bootstrap_extensions` | Removed unsupported CompositeLogger type for v1.30 | [RCA-001](./exercises/01-terraform-proxy/RCA-001-envoy-crashloop.md) |

## Prerequisites

- Minikube running (`minikube start`)
- `kubectl`, `terraform`, `ansible`, `helm` installed
- Python 3.10+

## Architecture

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Client    │────▶│  Envoy Proxy │────▶│  Backend    │
│  (curl)     │     │  (L7 router) │     │  (httpbin)  │
└─────────────┘     └──────┬───────┘     └─────────────┘
                           │
                    ┌──────▼───────┐
                    │  Prometheus  │
                    │  + Grafana   │
                    └──────────────┘
```

The proxy sits in front of a simple backend (httpbin), exposes Prometheus metrics, and Grafana visualizes them. Terraform deploys the infra, Ansible templates the config, Python scripts automate operations.
