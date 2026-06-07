# Exercise 03: Envoy L7 Path-Based Routing

> Prerequisite: Exercise 01 completed (envoy-proxy + httpbin running in proxy-lab namespace)

---

## Objective

Add **path-based routing** to Envoy so different URL paths go to different backends:

```
/api/*  → httpbin (API backend)
/       → nginx (static/frontend)
```

---

## Architecture

```
Client
  │
  ▼
Envoy Proxy (:8080)
  │
  ├── /api/* ──→ httpbin:80 (with prefix_rewrite: strips /api/)
  │
  └── /*     ──→ nginx:80
```

---

## Key Concepts

### 1. Service names create DNS in Kubernetes

When you create a Service with `name: nginx-backend` in `namespace: proxy-lab`, K8s creates:

```
nginx-backend.proxy-lab.svc.cluster.local
```

Envoy uses this DNS name to find backends. **If you change the Service name, Envoy gets 503.**

### 2. What names matter?

| Name | Where it's used | If you change it... |
|------|----------------|---------------------|
| `name` in Service metadata | Creates DNS record | Envoy can't resolve backend → 503 |
| `name` in ConfigMap metadata | Pod mounts this by name | Pod crash → CrashLoopBackOff |
| `app: X` label | Service selector finds pods | Service routes to nothing |
| `cluster: X` in Envoy config | Internal reference for routing | Routing breaks silently |
| **Filename** (backends.yaml) | **Doesn't matter** | Just for you |

### 3. Envoy routing order matters

Routes are evaluated **top to bottom**. Put more specific paths first:

```yaml
routes:
  - match: { prefix: "/api/" }   # ← More specific first
    route: { cluster: httpbin }
  - match: { prefix: "/" }       # ← Catch-all last
    route: { cluster: nginx }
```

If you put `/` first, everything would go to nginx (never reaches `/api/`).

### 4. prefix_rewrite

```yaml
- match:
    prefix: "/api/"
  route:
    cluster: httpbin_backend
    prefix_rewrite: "/"          # Strips /api/ before sending to backend
```

Client calls: `GET /api/users`
httpbin receives: `GET /users`

Without rewrite, httpbin would receive `/api/users` and might return 404.

### 5. The kubectl apply warning

```
Warning: resource configmaps/envoy-config is missing the kubectl.kubernetes.io/last-applied-configuration annotation
```

**Why:** The ConfigMap was originally created by Terraform (not kubectl). K8s patches the annotation automatically. Harmless.

**Lesson:** When mixing Terraform + kubectl on the same resource, you'll see this warning. In production, choose one tool per resource.

### 6. Why `kubectl rollout restart`?

Envoy reads its config **only at startup**. It does NOT hot-reload ConfigMaps automatically.

```
1. You update ConfigMap → K8s stores it ✅
2. But the running pod still has the OLD config in memory
3. `rollout restart` tells K8s: "kill old pod, create new one"
4. New pod starts and mounts the UPDATED ConfigMap
5. `rollout status` waits until new pod is Ready
```

**Alternatives to rollout restart:**
| Method | How it works | When to use |
|--------|-------------|-------------|
| `rollout restart` | Kill pod, new one reads fresh config | Simple, what we use here |
| Envoy xDS (dynamic config) | Config server pushes updates to Envoy at runtime | Istio, production service mesh |
| Reloader (k8s controller) | Watches ConfigMaps, auto-restarts pods on change | Medium complexity, popular in prod |
| SIGHUP / hot-restart | Signal Envoy process to reload | Not applicable with mounted ConfigMaps |

**For interviews:** "Envoy reads config at boot. To apply ConfigMap changes, I restart the deployment. In production with Istio, you'd use xDS for zero-downtime config updates."

---

## Files

| File | Purpose |
|------|---------|
| `backends.yaml` | Creates nginx-backend Deployment + Service |
| `envoy-routing-config.yaml` | Updated ConfigMap with path-based routing (2 clusters) |

---

## Steps

```bash
# 1. Create nginx backend
kubectl apply -f backends.yaml

# 2. Verify pods
kubectl get pods -n proxy-lab
# Expected: envoy-proxy, httpbin, nginx-backend all Running

# 3. Update Envoy config with path-based routing
kubectl apply -f envoy-routing-config.yaml

# 4. Restart Envoy to pick up new config
kubectl rollout restart deployment envoy-proxy -n proxy-lab

# 5. Wait for rollout
kubectl rollout status deployment envoy-proxy -n proxy-lab

# 6. Test: /api/ goes to httpbin
kubectl run curl-test --rm -it --image=curlimages/curl --restart=Never -n proxy-lab \
  -- curl -s http://envoy-proxy:8080/api/get

# 7. Test: / goes to nginx
kubectl run curl-test2 --rm -it --image=curlimages/curl --restart=Never -n proxy-lab \
  -- curl -s http://envoy-proxy:8080/
```

---

## Expected Results

**Test /api/get → httpbin:**
```json
{
  "args": {},
  "headers": {
    "Accept": "*/*",
    "Host": "envoy-proxy:8080",
    "User-Agent": "curl/8.20.0",
    "X-Envoy-Expected-Rq-Timeout-Ms": "15000",
    "X-Envoy-Original-Path": "/api/get"
  },
  "origin": "10.244.1.11",
  "url": "http://envoy-proxy:8080/get"
}
```

**What to notice:**
- `X-Envoy-Original-Path: /api/get` — Envoy saved the original path before rewriting
- `"url": ".../get"` — httpbin received `/get` not `/api/get` → `prefix_rewrite` worked
- `X-Envoy-Expected-Rq-Timeout-Ms` — Envoy injects timeout headers automatically

**Test / → nginx:**
```html
<!DOCTYPE html>
<html>
<head><title>Welcome to nginx!</title></head>
<body>
<h1>Welcome to nginx!</h1>
...
</body>
</html>
```

**What to notice:**
- Same proxy (envoy:8080), different path → completely different backend
- This is L7 routing — the proxy inspects the HTTP path (not just IP/port)

---

## Understanding the curl pattern

```bash
kubectl run test1 --rm -it --image=curlimages/curl --restart=Never -n proxy-lab \
  -- curl -s http://envoy-proxy:8080/api/get
```

| Flag | What it does |
|------|-------------|
| `run test1` | Creates a pod named "test1" |
| `--rm` | **Auto-delete pod when done** (no leftover Completed pods) |
| `-it` | Interactive + TTY (see output in real time) |
| `--image=curlimages/curl` | Lightweight image with curl installed |
| `--restart=Never` | One-shot pod (don't restart if it exits) |
| `-n proxy-lab` | Run in the same namespace (can resolve Service DNS) |
| `-- curl -s ...` | The command to run inside the pod |

**Why this pattern?**
- You can't curl ClusterIP services from outside the cluster
- This creates a temporary pod INSIDE the cluster that can reach internal services
- `--rm` cleans up automatically (unlike the `curl-admin` pod we left behind earlier)

**Without `--rm`:**
```bash
kubectl get pods -n proxy-lab
# curl-admin   0/1   Completed   0   5h  ← zombie pod, wastes nothing but clutters output
```

---

## What this demonstrates (for interviews)

- **L7 routing:** Different paths → different backends (like API Gateway)
- **Service discovery:** Envoy uses K8s DNS (Service names) to find backends
- **Config-driven routing:** Change routing without redeploying code
- **prefix_rewrite:** Clean URL transformation at the proxy layer

> "I configured Envoy as an L7 proxy with path-based routing in Kubernetes.
> /api requests go to one backend, static content to another.
> All config-driven via ConfigMap — no code changes needed to change routing."
