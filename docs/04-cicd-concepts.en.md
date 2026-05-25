# 04 — CI/CD: Pipelines, GitOps & Deployment Strategies

> Covers GitHub Actions, GitOps, ArgoCD, deployment strategies, and pipeline security.
> Focused on real-world scenarios frequently asked in EPAM technical interviews.

---

## Index

1. [The Big Picture: CI vs CD vs GitOps](#1-the-big-picture)
2. [GitHub Actions: Workflow Anatomy](#2-github-actions)
3. [Buildspec: AWS CodeBuild](#3-buildspec-aws-codebuild)
4. [Docker in Pipelines: Build, Tag, Push](#4-docker-in-pipelines)
5. [Deployment Strategies](#5-deployment-strategies)
6. [GitOps with ArgoCD](#6-gitops-with-argocd)
7. [Pipeline Security](#7-pipeline-security)
8. [Rollback: Manual and Automatic](#8-rollback-manual-and-automatic)
9. [Interview Questions with Answer Key](#9-interview-questions)

---

## 1. The Big Picture

```
Developer pushes code
        │
        ▼
┌───────────────┐
│      CI       │  Continuous Integration
│               │  - Code checkout
│               │  - Docker image build
│               │  - Unit / Integration tests
│               │  - Security scanning (Trivy, SAST)
│               │  - Push to ECR / registry
└───────┬───────┘
        │ image tagged with commit SHA
        ▼
┌───────────────┐
│      CD       │  Continuous Delivery / Deployment
│               │  - Update K8s manifest
│               │  - Apply to cluster (kubectl / ArgoCD)
│               │  - Verify deployment health
│               │  - Automatic rollback on failure
└───────────────┘
```

### CI vs CD vs GitOps

| | CI | Traditional CD | GitOps |
|--|---|---|---|
| **What it does** | Build + test + push image | Pipeline running `kubectl apply` | Git is the single source of truth; an agent synchronizes |
| **Who applies changes** | Pipeline | Pipeline (push) | Agent inside the cluster (pull) |
| **Audit** | Pipeline logs | Pipeline logs | Git history = full audit trail |
| **Rollback** | Manual or script | Manual or script | `git revert` → automatic |
| **Example** | GitHub Actions | CodePipeline + CodeDeploy | ArgoCD, Flux |

---

## 2. GitHub Actions

### Workflow Anatomy

```yaml
# .github/workflows/ci-cd.yml

name: CI/CD Pipeline          # Visible name in GitHub UI

on:                            # Triggers
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:           # Manual trigger from UI

env:                           # Global workflow variables
  AWS_REGION: us-east-1
  ECR_REPO: my-company/my-app

jobs:
  test:                        # job 1: tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Run tests
        run: |
          npm install
          npm test

  build-and-push:              # job 2: build image
    needs: test                # waits for "test" to succeed
    runs-on: ubuntu-latest
    outputs:
      image-tag: ${{ steps.meta.outputs.tags }}

    steps:
      - uses: actions/checkout@v4

      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}   # OIDC, no access keys
          aws-region: ${{ env.AWS_REGION }}

      - name: Login to ECR
        id: login-ecr
        uses: aws-actions/amazon-ecr-login@v2

      - name: Build, tag & push
        id: meta
        env:
          REGISTRY: ${{ steps.login-ecr.outputs.registry }}
          IMAGE_TAG: ${{ github.sha }}
        run: |
          docker build -t $REGISTRY/$ECR_REPO:$IMAGE_TAG .
          docker push $REGISTRY/$ECR_REPO:$IMAGE_TAG
          echo "tags=$REGISTRY/$ECR_REPO:$IMAGE_TAG" >> $GITHUB_OUTPUT

  deploy:                      # job 3: deploy to EKS
    needs: build-and-push
    runs-on: ubuntu-latest
    environment: production    # requires manual approval if configured

    steps:
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v4
        with:
          role-to-assume: ${{ secrets.AWS_ROLE_ARN }}
          aws-region: ${{ env.AWS_REGION }}

      - name: Update kubeconfig
        run: aws eks update-kubeconfig --name my-cluster --region $AWS_REGION

      - name: Deploy to EKS
        env:
          IMAGE_TAG: ${{ needs.build-and-push.outputs.image-tag }}
        run: |
          kubectl set image deployment/my-app app=$IMAGE_TAG
          kubectl rollout status deployment/my-app --timeout=300s
```

### Key GitHub Actions Concepts

**Triggers (`on`)**:
```yaml
on:
  push:
    branches: [main, release/*]
    paths: ['src/**', 'Dockerfile']   # only if these files change
  schedule:
    - cron: '0 2 * * *'              # nightly build at 2 AM
  workflow_dispatch:                  # manual trigger
```

**Secrets and Variables**:
```yaml
# Secrets: encrypted, never visible in logs
${{ secrets.AWS_ROLE_ARN }}
${{ secrets.DB_PASSWORD }}

# Variables: visible, for non-sensitive config
${{ vars.AWS_REGION }}
${{ vars.ECR_REPO }}

# Automatic GitHub Context variables
${{ github.sha }}          # Commit SHA
${{ github.ref_name }}     # Branch name
${{ github.actor }}        # User who pushed
${{ github.repository }}   # org/repo
```

**Environments**: Protect production deployments.
```yaml
jobs:
  deploy-prod:
    environment: production   # blocks until a reviewer approves in GitHub UI
```

**Reusable Workflows**: Avoid duplicating pipelines across repositories.
```yaml
# Call a workflow defined in another repo or file
jobs:
  call-shared-pipeline:
    uses: my-company/shared-workflows/.github/workflows/deploy.yml@main
    with:
      environment: production
      cluster-name: my-cluster
    secrets: inherit
```

**Matrix Strategy**: Run the same job with multiple configurations.
```yaml
jobs:
  test:
    strategy:
      matrix:
        node-version: [18, 20, 22]
        os: [ubuntu-latest, windows-latest]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
      - run: npm test
```

---

## 3. Buildspec: AWS CodeBuild

When using AWS CodePipeline instead of GitHub Actions, the build is defined in `buildspec.yml`.

```yaml
# buildspec.yml (at the root of the repo)
version: 0.2

env:
  variables:
    AWS_REGION: us-east-1
  parameter-store:               # read secrets from Parameter Store
    DB_PASSWORD: /prod/db/password

phases:
  install:                       # install build dependencies
    runtime-versions:
      nodejs: 20
    commands:
      - npm install -g yarn

  pre_build:                     # before build: login, setup
    commands:
      - echo Logging into ECR...
      - aws ecr get-login-password --region $AWS_REGION |
          docker login --username AWS --password-stdin $ECR_REGISTRY
      - IMAGE_TAG=$(echo $CODEBUILD_RESOLVED_SOURCE_VERSION | cut -c1-7)

  build:                         # the actual build
    commands:
      - echo Build started at $(date)
      - docker build -t $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG .
      - docker push $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG

  post_build:                    # after build: notifications, artifacts
    commands:
      - echo Build completed
      - printf '[{"name":"my-app","imageUri":"%s"}]'
          $ECR_REGISTRY/$ECR_REPO:$IMAGE_TAG > imagedefinitions.json

artifacts:                       # files passed to the next pipeline stage
  files:
    - imagedefinitions.json
    - appspec.yml

cache:                           # cache node_modules between builds (faster)
  paths:
    - node_modules/**/*
```

---

## 4. Docker in Pipelines

### Tag Strategy: How to name images

```bash
# Never use only :latest in production — you don't know which version it is

# ✅ Use the commit SHA (immutable, traceable)
IMAGE_TAG=my-app:abc1234

# ✅ Or combine with a date for readability
IMAGE_TAG=my-app:2024-01-15-abc1234

# ✅ For releases: use the Git tag
IMAGE_TAG=my-app:v1.2.3

# The SHA guarantees:
# - Reproducibility: you always know exactly which code is running
# - Traceability: from pod to commit in 2 steps
# - Exact Rollback: kubectl set image ... my-app:abc1232 (the previous commit)
```

### Multi-stage Build: Smaller and safer images

```dockerfile
# Stage 1: build (large image, contains compilers, dev tools)
FROM node:20 AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci --only=production
COPY . .
RUN npm run build

# Stage 2: runtime (minimal image, only what's necessary)
FROM node:20-alpine AS runtime
WORKDIR /app

# Only copy the build output, not the source code
COPY --from=builder /app/dist ./dist
COPY --from=builder /app/node_modules ./node_modules

# Do not run as root
RUN addgroup -S appgroup && adduser -S appuser -G appgroup
USER appuser

EXPOSE 3000
CMD ["node", "dist/server.js"]
```

> 💡 **Why it matters for interviews**: smaller image = smaller attack surface,
> less pull time, lower storage costs in ECR. Not running as root is a
> Pod Security Standards requirement in K8s.

---

## 5. Deployment Strategies

### Rolling Update (K8s default)

Replaces pods one by one. Zero downtime if you use `minReadySeconds` and readiness probes.

```yaml
spec:
  replicas: 4
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 1         # 1 extra pod allowed during update
      maxUnavailable: 0   # never kill a pod before the new one is Ready
```

```
Before: [v1] [v1] [v1] [v1]
Step 1: [v1] [v1] [v1] [v2]   ← v2 starts, passes readiness probe
Step 2: [v1] [v1] [v2] [v2]   ← v1 is terminated
Step 3: [v1] [v2] [v2] [v2]
Step 4: [v2] [v2] [v2] [v2]
```

**When to use it**: Most cases. Versions are compatible with each other.
**Risk**: If v2 has a bug, there is a period where v1 and v2 run simultaneously.

---

### Blue/Green

Two complete environments. Instant traffic switch.

```
Blue (v1) ←── Service (selector: version=blue)    ACTIVE
Green (v2) ←── no traffic                        ON STANDBY

# Step 1: deploy green (without traffic)
kubectl apply -f deployment-green.yaml

# Step 2: verify green is healthy
kubectl rollout status deployment/app-green

# Step 3: instant switch
kubectl patch service my-app -p '{"spec":{"selector":{"version":"green"}}}'

# Step 4: if it fails, revert in seconds
kubectl patch service my-app -p '{"spec":{"selector":{"version":"blue"}}}'
```

**When to use it**: Database changes, breaking API changes, when you need
instant rollback.  
**Cost**: Requires double the resources during the switch.

---

### Canary

Sends a small percentage of traffic to the new version. Monitor. Gradually increase.

```yaml
# With Argo Rollouts (the cleanest way in K8s)
apiVersion: argoproj.io/v1alpha1
kind: Rollout
metadata:
  name: my-app
spec:
  replicas: 10
  strategy:
    canary:
      steps:
        - setWeight: 10        # 10% traffic to new version
        - pause: {duration: 5m}
        - setWeight: 30
        - pause: {duration: 5m}
        - analysis:             # automatic metrics analysis
            templates:
              - templateName: success-rate
        - setWeight: 100        # if analysis passed, 100%
```

```
Traffic: 90% → [v1][v1][v1][v1][v1][v1][v1][v1][v1]
          10% → [v2]

If metrics OK → 70/30 → 0/100
If metrics bad → automatic rollback to 100% v1
```

**When to use it**: When you want to validate v2 with real traffic before doing the
full switch. Ideal for features with conversion or performance impact.

---

### Interview Comparison

| | Rolling | Blue/Green | Canary |
|--|---|---|---|
| **Downtime** | None | None | None |
| **Rollback** | Slow (re-roll) | Instant | Automatic if analysis is set |
| **Extra Resources** | Minimal | 2x during switch | Minimal (only % canary) |
| **Complexity** | Low | Medium | High |
| **Mixed Version Risk** | Yes (transient) | No | Yes (intentional) |
| **Ideal for** | Most cases | Critical / DB changes | Real traffic validation |

---

## 6. GitOps with ArgoCD

### The problem it solves

In traditional CD, the pipeline has direct cluster access (`kubectl apply`).
Issues:
- The pipeline needs cluster credentials
- If someone runs `kubectl apply` manually, cluster state diverges from the repo
- No easy way to know *what* is running vs *what should* be running

**GitOps**: Git is the single source of truth. An agent *inside* the cluster synchronizes state.

```
Developer → Git PR → merge → ArgoCD detects change → applies to cluster
                                       ↑
                               (pull, not push)
                               ArgoCD is already inside
                               No external credentials needed
```

### Key ArgoCD Concepts

**Application**: The primary ArgoCD object. Defines what to sync and where.

```yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: my-app
  namespace: argocd
spec:
  project: default

  source:
    repoURL: https://github.com/my-company/k8s-manifests
    targetRevision: main
    path: apps/my-app/overlays/prod    # folder with manifests

  destination:
    server: https://kubernetes.default.svc   # local cluster
    namespace: production

  syncPolicy:
    automated:
      prune: true      # removes resources no longer in Git
      selfHeal: true   # if someone modifies manually, ArgoCD reverts
    syncOptions:
      - CreateNamespace=true
```

**Sync Status**:
- `Synced`: cluster == Git ✅
- `OutOfSync`: manual modification or new change in Git
- `Degraded`: resources with errors (pods crashing, etc.)

**App of Apps pattern**: An Application that manages other Applications.
```
argocd/
  app-of-apps.yaml          ← Application pointing to apps/
  apps/
    frontend.yaml            ← Application for frontend
    backend.yaml             ← Application for backend
    monitoring.yaml          ← Application for monitoring stack
```

### Full GitOps Workflow

```
1. Developer creates PR with image change in deployment.yaml
   (image: my-app:abc1234  →  my-app:def5678)

2. PR review + merge to main

3. ArgoCD detects change in repo (polling every 3 min or webhook)

4. ArgoCD calculates diff between Git and cluster

5. ArgoCD applies change (internal kubectl apply)

6. ArgoCD monitors for successful rollout

7. If failure: ArgoCD can automatically rollback to previous commit

8. Git history = full audit trail of who changed what and when
```

### Image Promotion Between Environments

```
apps/
  my-app/
    base/
      deployment.yaml    ← image: my-app:PLACEHOLDER
    overlays/
      dev/
        kustomization.yaml  ← image: my-app:abc1234  (updated by CI)
      staging/
        kustomization.yaml  ← image: my-app:abc1234  (manual or auto)
      prod/
        kustomization.yaml  ← image: my-app:v1.2.3   (approved releases only)
```

CI pipeline automatically updates the `dev` overlay.
Promotion to `staging` and `prod` is a PR — with review and approval.

---

## 7. Pipeline Security

### Don't use Access Keys — use OIDC

```yaml
# BAD: hardcoded access keys in GitHub secrets
AWS_ACCESS_KEY_ID: AKIA...
AWS_SECRET_ACCESS_KEY: ...
# Rotated manually; if leaked, valid indefinitely

# GOOD: OIDC — GitHub Actions assumes an IAM Role directly
- name: Configure AWS credentials
  uses: aws-actions/configure-aws-credentials@v4
  with:
    role-to-assume: arn:aws:iam::123456789:role/github-actions-role
    aws-region: us-east-1
# Temporary credentials, automatic rotation, no secrets to manage
```

**Configuring OIDC in AWS**:
```hcl
# Terraform to create GitHub OIDC provider in AWS
resource "aws_iam_openid_connect_provider" "github" {
  url             = "https://token.actions.githubusercontent.com"
  client_id_list  = ["sts.amazonaws.com"]
  thumbprint_list = ["6938fd4d98bab03faadb97b34396831e3780aea1"]
}

resource "aws_iam_role" "github_actions" {
  name = "github-actions-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.github.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringLike = {
          "token.actions.githubusercontent.com:sub" =
            "repo:my-company/my-repo:ref:refs/heads/main"
        }
      }
    }]
  })
}
```

### Image Scanning with Trivy

```yaml
- name: Scan image for vulnerabilities
  uses: aquasecurity/trivy-action@master
  with:
    image-ref: ${{ env.ECR_REGISTRY }}/${{ env.ECR_REPO }}:${{ github.sha }}
    format: 'sarif'
    output: 'trivy-results.sarif'
    severity: 'CRITICAL,HIGH'
    exit-code: '1'     # fails pipeline if CRITICAL or HIGH found
```

### Secrets Management in Pipelines

```
Never in code:            DB_PASS="super-secret"  ❌
Never in .env in Git:     .env with passwords       ❌

Correct options:
1. GitHub Actions Secrets  → for CI variables (role ARNs, etc.)
2. AWS Secrets Manager     → for application secrets at runtime
3. AWS Parameter Store     → for configuration and less critical secrets
4. External Secrets Op.    → automatically syncs Secrets Manager → K8s Secrets
```

---

## 8. Rollback: Manual and Automatic

### Manual Rollback in K8s

```bash
# View deployment version history
kubectl rollout history deployment/my-app

# Rollback to previous version
kubectl rollout undo deployment/my-app

# Rollback to specific version
kubectl rollout undo deployment/my-app --to-revision=3

# Verify rollback progress
kubectl rollout status deployment/my-app

# See which image is currently running
kubectl get deployment my-app -o jsonpath='{.spec.template.spec.containers[0].image}'
```

### Automatic Rollback in GitHub Actions

```yaml
- name: Deploy and verify
  run: |
    kubectl set image deployment/my-app app=$IMAGE_TAG
    
    # Wait up to 5 minutes for successful rollout
    if ! kubectl rollout status deployment/my-app --timeout=300s; then
      echo "Deployment failed — rolling back"
      kubectl rollout undo deployment/my-app
      kubectl rollout status deployment/my-app
      exit 1   # mark pipeline as failed
    fi
```

### Rollback with ArgoCD (GitOps)

```bash
# View ArgoCD sync history
argocd app history my-app

# Rollback to previous sync (pointing to a Git commit)
argocd app rollback my-app --revision 3

# Or simply: git revert + push → ArgoCD syncs automatically
git revert HEAD
git push origin main
# ArgoCD detects new commit and applies the revert
```

> 💡 **Correct interview answer**: In GitOps, rollback is a `git revert`.
> It's not a kubectl or ArgoCD command — it's a Git operation that stays audited.

---

## 9. Interview Questions

**"What is the difference between CI and CD?"**

```
CI (Continuous Integration):
- Triggered on every push or PR
- Validates that code integrates correctly with the rest
- Build + test + static analysis + security scanning
- Produces an artifact (Docker image) ready for deployment

CD (Continuous Delivery):
- Takes the CI artifact and deploys it to an environment
- Can be automatic (Continuous Deployment) or require manual approval
- Verifies successful deployment
- Includes rollback if failure occurs

Key difference: CI validates code. CD deploys it.
You can have CI without CD (building but deploying manually).
```

---

**"How do you implement automatic rollback if deployment fails?"**

```
There are three layers of protection:

1. K8s Readiness Probe:
   - If new pod fails readiness probe, K8s stops sending traffic
   - Rolling update stops automatically
   - Old pods stay active

2. kubectl rollout status in pipeline:
   if ! kubectl rollout status deployment/my-app --timeout=300s; then
     kubectl rollout undo deployment/my-app
     exit 1
   fi

3. With ArgoCD + Argo Rollouts:
   - Automatic metrics analysis (error rate, latency) during canary
   - If metrics exceed threshold → automatic rollback without human intervention

rollout status is the MVP. In real production, metrics analysis
provides actual confidence that the new version is healthy.
```

---

**"What is GitOps and how does it differ from traditional CD pipelines?"**

```
Traditional CD (push):
- Pipeline has cluster credentials
- Runs kubectl apply directly
- If someone modifies cluster manually, pipeline doesn't know
- Audit: pipeline logs (hard to follow)

GitOps (pull):
- Git is the absolute source of truth
- An agent (ArgoCD) INSIDE the cluster pulls from Git and applies
- If someone modifies cluster manually, ArgoCD detects and reverts (selfHeal)
- Audit: Git history = who changed what, when, why (commit message + PR)
- Rollback = git revert (standard, audited operation)
- Cluster is never ahead of Git

Key advantages:
1. Security: no cluster credentials outside the cluster
2. Consistency: cluster always converges to Git state
3. Auditability: full history in Git
4. Disaster recovery: if cluster is lost, ArgoCD rebuilds from Git
```

---

**"When would you use Canary vs Blue/Green?"**

```
Blue/Green when:
- Change is a database migration (clean switch needed)
- Breaking API changes and instant rollback needed
- Validating in an identical environment before switch
- Validation time is short (seconds or minutes)
Cost: Double resources during switch period

Canary when:
- Validating real impact with a subset of users
- Change affects performance/behavior seen only with real traffic
- Clear success metrics (error rate, latency, conversion rate)
- Tolerating a % of users experiencing the new version
Advantage: Detect issues before affecting all users
```

---

**"How do you ensure secrets don't leak in the pipeline?"**

```
Four levels of protection:

1. Never in code or .env in Git

2. In GitHub Actions: Use OIDC instead of access keys
   → No AWS secrets to manage, credentials are temporary

3. At runtime (the app): Use AWS Secrets Manager + External Secrets Operator
   → Secrets never pass through the pipeline; go directly from AWS to pod

4. CI Secret Scanning:
   - GitLeaks: detects if someone accidentally committed a secret
   - git-secrets: pre-commit hook that blocks push if AWS key patterns found

5. If leaked: rotate immediately, audit CloudTrail, revoke GitHub token
```

---

**"A deployment went wrong and users are affected. What do you do?"**

```
Priority 1: Mitigate (don't investigate yet)

1. When was the last deploy? 
   → If recent: kubectl rollout undo deployment/my-app
   → Verify: kubectl rollout status deployment/my-app

2. Did rollback resolve it?
   → Check dashboards: error rate, latency
   → Confirm with support that users are operational

3. Communicate (while one tech does rollback, another communicates):
   → Status page: "Investigating an issue, ETA 15 min"
   → Internal Slack/Teams: current status, who's working on it

Priority 2: Investigate (AFTER mitigation)
   → kubectl logs deployment/my-app --previous
   → Review metrics from incident period
   → git diff between last good and failed commit

Priority 3: Post-mortem (within 48h)
   → Blameless, 5 Whys, action items with owner and date
```

---

## 📖 Navigation

- **⬅️ Previous:** [03-terraform-concepts.en.md](./03-terraform-concepts.en.md) — Advanced Terraform
- **➡️ Next:** [05-observability-concepts.en.md](./05-observability-concepts.en.md) — Observability
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
