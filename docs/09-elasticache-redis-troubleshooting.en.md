# 🛠️ SRE Deep Dive: ElastiCache Redis, TLS & VPC Isolation

This guide documents a real-world Senior SRE use case, demonstrating the ability to perform surgical interventions on AWS-managed databases (ElastiCache) under strict network security constraints (VPC), in-transit encryption (TLS), and orchestration (EKS).

[Versión en Español](./09-elasticache-redis-troubleshooting.md) | [Back to Dashboard](../MACR/00-DASHBOARD.md)

---

## 📖 Context (The Business Problem)

**Application:** LibreChat (Conversational AI platform backed by AWS Bedrock).  
**The Incident:** After an application update (or an AI agent state issue), user sessions stored in **Redis** became corrupted/inconsistent, blocking access.  
**The SRE Objective:** Surgically purge corrupted sessions in Redis without affecting the primary database (RDS Postgres), without causing massive downtime (avoiding `FLUSHALL`), and without breaching security protocols.

---

## 🧱 Sandbox Architecture (The SRE Challenge)

The environment featured high complexity and technical debt:

- **Network Isolation (VPC):** Redis ElastiCache was deployed in private subnets with no public access or direct routes from developers' VPNs.
- **Security (TLS In-Transit):** Due to compliance, ElastiCache required TLS for all connections; non-TLS `redis-cli` connections were rejected.
- **Data Architecture (Cluster Mode):** Redis was in **Cluster Mode Enabled**, with data sharded across multiple nodes.
- **Frontend Access Layer (ALB/ACM):** Web traffic entered via an ALB managed by the AWS Load Balancer Controller in EKS, using ACM certificates for SSL termination.
- **Soft Multi-tenancy (Namespace Isolation):** Sandbox and Staging coexisted in the **same EKS cluster**, separated only by Namespaces, increasing the blast radius for cluster-level errors.
- **CI/CD Fragility (The "Fork" and ECR):** The application was a highly customized fork (`mhchat`). Pushes to Amazon ECR used unstable tags without strict versioning, making automatic code-level rollbacks impossible.

---

## 🔬 Step-by-Step Technical Execution (The Intervention)

Resolving the incident required more than a single command; it involved building a secure access path to Redis within the VPC and correctly operating on a TLS/Cluster Mode cluster.

### Step 1: The Bridge (Kubernetes Port-Forwarding & Bastion Pod)

*   **Constraint:** The private ElastiCache IP was not accessible from my laptop.
*   **Decision:** Use Kubernetes as a bastion within the same VPC/namespace.
*   **Execution:** Deployed an ephemeral debug pod (alpine container with `redis-cli`) in the application's namespace.

```bash
kubectl run redis-debugger \
  --image=redis:alpine \
  --restart=Never -i --tty -- sh
```

### Step 2: The Certificate Barrier (TLS Handshake)

*   **Constraint:** ElastiCache required TLS and a valid CA certificate; unencrypted connections were rejected.
*   **Decision:** Enable TLS on the client and ensure a trusted chain.
*   **Execution:** A non-TLS connection attempt failed immediately. The appropriate flag was enabled.

```bash
# THIS FAILS (Connection closed due to lack of encryption)
redis-cli -h master.librechat-redis.xxxx.use1.cache.amazonaws.com -p 6379

# The Solution: Enable TLS
redis-cli --tls \
  -h master.librechat-redis.xxxx.use1.cache.amazonaws.com \
  -p 6379
```

> **SRE Note:** If the debug pod lacks `ca-certificates`, the TLS handshake fails with `certificate verify failed`; installing or mounting root certificates is mandatory.

### Step 3: Navigating Sharding (The MOVED Error)

*   **Constraint:** Redis was in Cluster Mode, and the key could reside on any shard.
*   **Decision:** Enable cluster mode on the client to handle automatic redirections.
*   **Execution:** When running delete commands, Redis returned `MOVED 10.0.1.45:6379` errors. The `-c` flag was used.

```bash
# Cluster-aware connection
redis-cli -c --tls \
  -h master.librechat-redis.xxxx.use1.cache.amazonaws.com \
  -p 6379
```
This allows the client to jump between internal nodes and purge exactly the problematic keys without touching the rest of the dataset.

### Step 4: Final Validation (ALB & Ingress)

*   After purging sessions, I verified that the L7 layer (ALB + Ingress Controller) continued routing HTTPS traffic only to healthy pods after the rollout.
*   Audited ACM certificates, Ingress rules, and ALB health checks to ensure no regressions in the entry layer.

---

## 🎤 The Narrative (How to tell it in Interviews)

**Situation:** *"At MHE, I inherited a customized fork of LibreChat (`mhchat`) on an EKS cluster with high technical debt: unstable CI/CD in ECR and soft isolation (Namespaces). After a push, Redis sessions became inconsistent."*

**Task:** *"I needed to surgically purge the cache without causing downtime in Staging or breaking VPC network policies."*

**Action:** *"I deployed a debug pod in EKS as a bastion and used `kubectl port-forward`. I navigated AWS security by enabling TLS and Cluster Mode in `redis-cli` to handle shard redirections, while auditing the ALB and ACM to ensure HTTPS entry."*

**Result & Next Steps:** *"I achieved hot stability. This success in the pioneer environment (Sandbox) allowed us to parameterize the infrastructure and promote the stack to Staging in a clean, automated way."*
