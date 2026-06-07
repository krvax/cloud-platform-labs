# Lab 19: Hybrid Cloud Networking (Simulated in Minikube)

> Prep for: Deloitte técnica (Viernes 29 Mayo, 11:30 AM)
> Focus: VPC concepts, network isolation, routing between environments, VPN simulation
> Runtime: Minikube (local K8s)

---

## Objective

Simulate a **hybrid cloud** scenario in Kubernetes:
- **Namespace `cloud-vpc`** = your cloud environment (like AWS VPC)
- **Namespace `onprem-dc`** = your on-premise datacenter
- **Network Policy** = simulates firewall rules (like Security Groups / NACLs)
- **Cross-namespace communication** = simulates VPN/Direct Connect routing

This demonstrates the same concepts you'd explain in an interview about connecting on-prem to cloud.

---

## Architecture

```
┌─────────────────────────────────┐     ┌─────────────────────────────────┐
│  Namespace: cloud-vpc           │     │  Namespace: onprem-dc           │
│  (simulates AWS VPC)            │     │  (simulates on-prem datacenter) │
│                                 │     │                                 │
│  ┌───────────┐  ┌───────────┐  │     │  ┌───────────┐                  │
│  │  web-app  │  │  cloud-db │  │     │  │ legacy-app│                  │
│  │  (nginx)  │  │  (redis)  │  │     │  │ (httpbin) │                  │
│  └───────────┘  └───────────┘  │     │  └───────────┘                  │
│                                 │     │                                 │
└─────────────────────────────────┘     └─────────────────────────────────┘
              │                                       │
              └───── Cross-namespace DNS ─────────────┘
              (simulates VPN tunnel / Direct Connect)
```

---

## Key Concepts Demonstrated

| Real-world concept | What we simulate in K8s |
|-------------------|------------------------|
| VPC | Namespace with its own services |
| Subnet isolation | Network Policies blocking traffic |
| Security Groups | Network Policies (allow specific pods/ports) |
| VPN / Direct Connect | Cross-namespace Service DNS |
| Route Tables | K8s DNS resolution (`svc.namespace.svc.cluster.local`) |
| CIDR non-overlap | Different namespaces = different "networks" |

---

## Why this works as interview prep

In K8s, namespaces are **NOT** network-isolated by default (unlike VPCs). But with **Network Policies**, you can:
- Block all traffic by default (like a VPC with no routes)
- Allow specific traffic (like adding a VPN route or Security Group rule)
- Control ingress/egress per pod (like NACLs)

This gives you hands-on experience with the SAME mental model as VPC design.

---

## Steps

### Step 1: Create namespaces (the "environments")

```bash
kubectl apply -f namespaces.yaml
```

This creates:
- `cloud-vpc` — represents your cloud VPC
- `onprem-dc` — represents your on-prem datacenter

### Step 2: Deploy apps in each "environment"

```bash
kubectl apply -f cloud-apps.yaml
kubectl apply -f onprem-apps.yaml
```

### Step 3: Verify cross-namespace communication works (no isolation yet)

```bash
# From cloud-vpc, reach onprem-dc
kubectl run test --rm -it --image=curlimages/curl --restart=Never -n cloud-vpc \
  -- curl -s http://legacy-app.onprem-dc.svc.cluster.local/get
```

This works because K8s has NO network isolation by default.

### Step 4: Apply Network Policies (simulate firewall / VPC isolation)

```bash
kubectl apply -f network-policies.yaml
```

Now traffic is blocked by default — only explicitly allowed connections work.

### Step 5: Test isolation

```bash
# This should FAIL (blocked by policy)
kubectl run test --rm -it --image=curlimages/curl --restart=Never -n cloud-vpc \
  -- curl -s --max-time 3 http://legacy-app.onprem-dc.svc.cluster.local/get

# This should SUCCEED (allowed by policy — simulates "VPN route")
kubectl run test --rm -it --image=curlimages/curl --restart=Never -n cloud-vpc \
  -l access=vpn \
  -- curl -s http://legacy-app.onprem-dc.svc.cluster.local/get
```

### Step 6: Explain what happened (interview answer)

> "I isolated two namespaces with Network Policies — simulating VPC isolation.
> By default, no traffic flows between them (like two VPCs without peering).
> Then I allowed specific labeled pods to communicate — simulating a VPN tunnel
> that only authorized traffic can use."

---

## Files

| File | Purpose |
|------|---------|
| `namespaces.yaml` | Creates cloud-vpc and onprem-dc namespaces |
| `cloud-apps.yaml` | Deploys web-app (nginx) + cloud-db (redis) in cloud-vpc |
| `onprem-apps.yaml` | Deploys legacy-app (httpbin) in onprem-dc |
| `network-policies.yaml` | Default-deny + selective allow (simulates firewall rules) |

---

## Interview talking points from this lab

1. **"How do you isolate environments?"**
   > "In K8s I use Network Policies for namespace isolation. In AWS, separate VPCs with no peering by default."

2. **"How do you connect on-prem to cloud?"**
   > "Site-to-Site VPN or Direct Connect. In K8s terms, it's like allowing cross-namespace traffic only for specific labeled pods."

3. **"What's the difference between Security Groups and NACLs?"**
   > "SGs are stateful per-instance (like pod-level Network Policies). NACLs are stateless per-subnet (like namespace-wide deny rules)."

4. **"How do you ensure only authorized traffic flows?"**
   > "Default-deny everything, then explicitly allow what's needed. Least privilege at the network layer."

---

## Cleanup

```bash
kubectl delete namespace cloud-vpc onprem-dc
```

---

## How to Resume After WSL Restart

After restarting WSL or your machine, the cluster is stopped. To resume:

```bash
# 1. Start minikube (restores cluster state)
minikube start

# 2. Verify nodes are Ready
kubectl get nodes

# 3. Check if your pods are still running
kubectl get pods -n proxy-lab        # Lab 16
kubectl get pods -n cloud-vpc        # Lab 19
kubectl get pods -n onprem-dc        # Lab 19

# 4. If pods are gone (namespace deleted), re-apply:
cd ~/src/learning/interview-prep/epam-aws-devops/labs/lab-19-hybrid-cloud
kubectl apply -f namespaces.yaml
kubectl apply -f cloud-apps.yaml
kubectl apply -f onprem-apps.yaml
kubectl apply -f network-policies.yaml
```

**Key point:** `minikube start` preserves everything (namespaces, pods, services, policies). You only need to re-apply if you ran `kubectl delete` or `minikube delete`.

---

## What We Built Today (28 Mayo 2026)

### Lab 16 — Exercise 01: Terraform + Envoy Proxy ✅
- Terraform deploys Envoy + httpbin in minikube
- Fixed CrashLoopBackOff (invalid bootstrap_extensions)
- RCA documented

### Lab 16 — Exercise 03: Envoy L7 Path-Based Routing ✅
- Added nginx as second backend
- Envoy routes `/api/*` → httpbin, `/` → nginx
- Demonstrated prefix_rewrite and config-driven routing

### Lab 19 — Hybrid Cloud Networking ✅
- Created 2 namespaces (cloud-vpc + onprem-dc)
- Deployed apps in each "environment"
- Proved no isolation by default (cross-namespace curl works)
- Applied Network Policies (default-deny + selective allow)
- Proved isolation works (blocked without label, allowed with `access=vpn`)

### Interview value
> "I've built hands-on labs simulating hybrid cloud: VPC isolation with Network Policies,
> L7 proxy routing with Envoy, and IaC with Terraform modules. I can explain these
> concepts because I've implemented them, not just read about them."
