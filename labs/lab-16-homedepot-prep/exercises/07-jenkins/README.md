# Exercise 07: Jenkins in K8s + Shared Libraries + DORA Metrics

> Prerequisite: Prometheus + Grafana running in proxy-lab (Exercise 04)
> Tools: Helm, Jenkins, Prometheus Metrics Plugin
> Status: ✅ COMPLETED (28 Mayo 2026)

---

## Objective

Deploy Jenkins in minikube, create a pipeline with shared libraries, and monitor CI/CD metrics with Prometheus + Grafana (DORA metrics).

---

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│  Namespace: jenkins                                         │
│                                                             │
│  ┌──────────────────┐         ┌──────────────────────────┐ │
│  │    Jenkins        │         │  Prometheus              │ │
│  │    Controller     │────────▶│  (scrapes /prometheus/)  │ │
│  │    :8080 (UI)     │         └──────────┬───────────────┘ │
│  │    :50000 (agent) │                    │                 │
│  └──────────────────┘                    ▼                 │
│         ▲                        ┌──────────────────┐      │
│         │ JNLP                   │    Grafana        │      │
│  ┌──────┴───────┐               │  (DORA dashboard) │      │
│  │  K8s Agent   │               └──────────────────┘      │
│  │  (ephemeral) │                                          │
│  └──────────────┘                                          │
└─────────────────────────────────────────────────────────────┘
```

---

## Key Concepts

### Jenkins uses StatefulSet (NOT Deployment)

| | Deployment | StatefulSet |
|---|-----------|-------------|
| Pod name | `jenkins-abc123` (random) | `jenkins-0` (fixed) |
| Volume | Shared or ephemeral | One per pod (individual PVC) |
| Startup order | All at once | One by one (0, then 1, then 2) |
| DNS | Only via Service | Pod has own DNS: `jenkins-0.jenkins.ns.svc` |
| Use case | APIs, proxies, workers | Databases, Jenkins, Kafka, Redis cluster |

**Why Jenkins needs StatefulSet:**
- Fixed pod name (`jenkins-0`) so agents always know where to connect
- Persistent volume for config/plugins (though we disabled it for lab)
- Stable network identity

### `kubectl rollout restart statefulset`

```bash
kubectl rollout restart statefulset jenkins -n jenkins
```

Same as `rollout restart deployment` but for StatefulSets. It:
1. Kills the pod
2. Creates a new one with the same name (`jenkins-0`)
3. Respects ordering guarantees
4. New pod mounts fresh config

**When to use:** After installing plugins via UI (Jenkins needs restart to load them).

### Without persistence = plugins lost on restart

⚠️ We disabled PVC (`persistence.enabled=false`) for lab simplicity. This means:
- Every time the pod restarts, plugins installed via UI are LOST
- Solution: install plugins via Helm `controller.installPlugins[]` (they get installed at boot)
- In production: ALWAYS use PVC or a custom Docker image with plugins pre-baked

### DORA Metrics

| Metric | What it measures | Jenkins metric |
|--------|-----------------|----------------|
| Deployment Frequency | How often you deploy | `jenkins_builds_total_build_count_total` |
| Lead Time for Changes | Commit → production | `jenkins_builds_duration_milliseconds_summary` |
| Change Failure Rate | % of deploys causing failure | `jenkins_builds_failed_build_count_total / total` |
| Mean Time to Recovery | How fast you fix failures | Time between failed and next success |

---

## Steps to Reproduce (from scratch)

### Step 1: Install Jenkins with Helm

```bash
helm repo add jenkins https://charts.jenkins.io
helm repo update

helm install jenkins jenkins/jenkins \
  --namespace jenkins --create-namespace \
  --set controller.serviceType=NodePort \
  --set persistence.enabled=false \
  --set controller.installPlugins[0]=workflow-aggregator:latest \
  --set controller.installPlugins[1]=git:latest \
  --set controller.installPlugins[2]=kubernetes:latest
```

**Note:** We do NOT include `prometheus` plugin here because it has dependency issues when installed via Helm init container. We install it via UI instead.

### Step 2: Wait for Jenkins to be Ready

```bash
kubectl get pods -n jenkins -w
# Wait for: jenkins-0   2/2   Running
```

### Step 3: Get admin password and URL

```bash
# Password
kubectl exec --namespace jenkins -it svc/jenkins -c jenkins -- /bin/cat /run/secrets/additional/chart-admin-password && echo

# URL (keep terminal open)
minikube service jenkins -n jenkins --url
```

### Step 4: Install Prometheus Metrics Plugin via UI

1. Open Jenkins URL in browser
2. Login: admin / (password from step 3)
3. Go to: **Manage Jenkins → Plugins → Available plugins**
4. Search: `Prometheus metrics`
5. Install it
6. Check "Restart Jenkins when installation is complete"

### Step 5: Verify Prometheus endpoint works

```bash
kubectl run prom-test --rm -it --image=curlimages/curl --restart=Never -n jenkins \
  -- sh -c 'curl -s -u admin:YOUR_PASSWORD http://jenkins:8080/prometheus/ | grep jenkins | head -10'
```

### Step 6: Create the pipeline

In Jenkins UI: **New Item → "terraform-proxy-pipeline" → Pipeline → paste this:**

```groovy
pipeline {
    agent any
    stages {
        stage('Checkout') {
            steps {
                echo '📥 Checking out infrastructure code...'
            }
        }
        stage('Terraform Init') {
            steps {
                echo '🔧 terraform init'
                echo 'Initializing providers: hashicorp/kubernetes'
            }
        }
        stage('Terraform Plan') {
            steps {
                echo '📋 terraform plan -var-file=envs/dev.tfvars'
                echo 'Plan: 6 to add, 0 to change, 0 to destroy'
            }
        }
        stage('Terraform Apply') {
            steps {
                echo '🚀 terraform apply -auto-approve'
                echo 'Apply complete! Resources: 6 added'
            }
        }
        stage('Verify Deployment') {
            steps {
                echo '✅ kubectl get pods -n proxy-lab'
                echo 'envoy-proxy: Running'
                echo 'httpbin: Running'
            }
        }
    }
    post {
        success { echo '🎉 Pipeline completed successfully!' }
        failure { echo '❌ Pipeline failed — check logs' }
    }
}
```

Click **Save → Build Now**.

### Step 7: Annotate Jenkins Service for Prometheus scraping

```bash
kubectl annotate service jenkins -n jenkins \
  prometheus.io/scrape="true" \
  prometheus.io/port="8080" \
  prometheus.io/path="/prometheus/"
```

### Step 8: Verify in Grafana

1. Open Grafana (the one already running in proxy-lab)
2. Go to **Explore → prometheus**
3. Search metric: `default_jenkins_builds`
4. You should see: build count, duration, health score

---

## What the pipeline does (explained)

```groovy
pipeline {              // Declarative pipeline block
    agent any           // "Run on any available agent" → K8s creates ephemeral pod

    stages {            // Ordered list of phases
        stage('X') {    // Each stage = visual block in Jenkins UI
            steps {     // What to execute in this stage
                echo '' // Shell-like commands
            }
        }
    }

    post {              // Runs AFTER all stages
        success { }    // Only if everything passed
        failure { }    // Only if something failed
    }
}
```

**What happens when you click "Build Now":**
1. Jenkins Controller receives build request
2. K8s plugin creates an ephemeral agent pod
3. Agent connects to controller via JNLP (port 50000)
4. Controller sends pipeline to agent
5. Agent executes each stage in order
6. Post actions run (success/failure)
7. Agent pod is DESTROYED (ephemeral)

---

## Lessons Learned / RCA

### Issue: Prometheus plugin won't install via Helm
- **Cause:** Plugin version `852.v2317db_a_17161` has unresolvable dependencies in the init container
- **Fix:** Install via UI after Jenkins boots (UI resolves dependencies automatically)
- **Production fix:** Use a custom Docker image with plugins pre-installed, or use `kube-prometheus-stack` with ServiceMonitor

### Issue: `rollout restart deployment jenkins` fails
- **Cause:** Jenkins uses StatefulSet, not Deployment
- **Fix:** `kubectl rollout restart statefulset jenkins -n jenkins`

### Issue: Prometheus can't scrape Jenkins cross-namespace
- **Cause:** Default Prometheus config only scrapes pods with annotations in discovered namespaces
- **Fix:** Annotate the Jenkins Service with `prometheus.io/scrape`, `/port`, `/path`

---

## How to Resume After WSL Restart

```bash
# 1. Start minikube
minikube start

# 2. Check Jenkins is running
kubectl get pods -n jenkins
# If jenkins-0 is Running → you're good (but plugins are lost without PVC)

# 3. If you need to reinstall:
helm upgrade jenkins jenkins/jenkins \
  --namespace jenkins \
  --set controller.serviceType=NodePort \
  --set persistence.enabled=false \
  --set controller.installPlugins[0]=workflow-aggregator:latest \
  --set controller.installPlugins[1]=git:latest \
  --set controller.installPlugins[2]=kubernetes:latest

# 4. Reinstall Prometheus plugin via UI
# 5. Recreate pipeline (paste Groovy from this README)
# 6. Re-annotate service:
kubectl annotate service jenkins -n jenkins \
  prometheus.io/scrape="true" \
  prometheus.io/port="8080" \
  prometheus.io/path="/prometheus/"
```

---

## Interview talking points

1. **"How do you manage CI/CD at scale?"**
   > "Jenkins with shared libraries for consistency, K8s agents for elastic scaling, and Prometheus for pipeline observability."

2. **"How do you measure DevOps performance?"**
   > "DORA metrics: deployment frequency, lead time, change failure rate, MTTR. I track them in Grafana dashboards fed by Jenkins + Prometheus."

3. **"Jenkins vs GitHub Actions?"**
   > "GitHub Actions for simpler workflows and OSS. Jenkins for enterprise: complex pipelines, shared libraries, on-prem integration, and full control over execution environment."

4. **"Why StatefulSet for Jenkins?"**
   > "Jenkins needs stable identity (jenkins-0), persistent storage for config/plugins, and a fixed DNS for agents to connect. StatefulSet provides all three."

5. **"How do you handle plugin management?"**
   > "In production, I'd use a custom Docker image with plugins pre-baked, or Configuration as Code (JCasC) to declare plugins declaratively. For labs, Helm installPlugins works."
