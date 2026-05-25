# Lab 10: GitOps with ArgoCD 🐙

[🇪🇸 Español](./README.md) | [🇬🇧 English](./README.en.md)

This lab demonstrates how to implement the GitOps methodology using ArgoCD. You will deploy applications automatically from a Git repository to a Kubernetes cluster using the "pull" model.

## 🎯 Objectives
- Install ArgoCD on a local `kind` cluster.
- Expose the ArgoCD UI using port-forwarding.
- Understand the GitOps "pull" vs "push" models.
- Deploy an application using an `Application` CRD.
- Deploy multiple applications automatically using `ApplicationSet` and the Directory Generator.

## 🛠️ Prerequisites
- Docker desktop running.
- `kind` (Kubernetes IN Docker) installed.
- `kubectl` configured.

---

## 1. Cluster Setup & ArgoCD Installation

### Create a local cluster
```bash
kind create cluster --name argocd-lab
kubectl cluster-info --context kind-argocd-lab
```

### Install ArgoCD
ArgoCD runs as a set of controllers inside its own namespace.

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

Wait for the pods to be ready:
```bash
kubectl get pods -n argocd -w
```

### Access the UI
Expose the ArgoCD server:
```bash
kubectl port-forward svc/argocd-server -n argocd 8080:443
```
Access `https://localhost:8080` in your browser. (Accept the self-signed certificate warning).

**Get the initial admin password:**
```bash
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d; echo
```
Login with username `admin` and the extracted password.

---

## 2. Deploying a Single Application

We will deploy a simple guestbook application from the official ArgoCD example repository.

Apply the following `Application` CRD:

```yaml
# apps/guestbook.yaml
apiVersion: argoproj.io/v1alpha1
kind: Application
metadata:
  name: guestbook
  namespace: argocd
spec:
  project: default
  source:
    repoURL: https://github.com/argoproj/argocd-example-apps.git
    targetRevision: HEAD
    path: guestbook
  destination:
    server: https://kubernetes.default.svc
    namespace: guestbook
  syncPolicy:
    automated:
      prune: true
      selfHeal: true
    syncOptions:
    - CreateNamespace=true
```

```bash
kubectl apply -f apps/guestbook.yaml
```

Check the UI to see the application syncing automatically.

---

## 3. Scaling with ApplicationSets

When you have multiple microservices, creating an `Application` manifest for each one becomes tedious. The `ApplicationSet` controller solves this by acting as a "factory" for Applications.

We will use the **Git Directory Generator**, which scans a Git repository for directories and automatically generates an Application for each directory it finds.

> **Note**: If your `argocd-applicationset-controller` is in `CrashLoopBackOff`, you might be missing the CRD. Apply it directly:
> `kubectl apply -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/crds/applicationset-crd.yaml`

Apply the ApplicationSet:

```yaml
# apps/appset-example.yaml
apiVersion: argoproj.io/v1alpha1
kind: ApplicationSet
metadata:
  name: cluster-addons
  namespace: argocd
spec:
  generators:
  - git:
      repoURL: https://github.com/argoproj/argocd-example-apps.git
      revision: HEAD
      directories:
      - path: apps/*
  template:
    metadata:
      name: '{{path.basename}}'
    spec:
      project: default
      source:
        repoURL: https://github.com/argoproj/argocd-example-apps.git
        targetRevision: HEAD
        path: '{{path}}'
      destination:
        server: https://kubernetes.default.svc
        namespace: '{{path.basename}}'
      syncPolicy:
        automated:
          prune: true
          selfHeal: true
        syncOptions:
        - CreateNamespace=true
```

```bash
kubectl apply -f apps/appset-example.yaml
```

Watch how ArgoCD automatically discovers and deploys every application inside the `apps/` directory of the remote repository!

---

## 🧹 Cleanup

```bash
kind delete cluster --name argocd-lab
```
