# Exercise 01: Deploy Envoy Proxy with Terraform

## Objective

Deploy an Envoy proxy to Kubernetes using Terraform with proper module structure, variables, and environment-specific tfvars.

## What You'll Practice

- Terraform modules (reusable proxy module)
- Variables and tfvars (dev vs prod configs)
- Kubernetes provider in Terraform
- Deploying a real L7 proxy to K8s

## Setup

```bash
cd exercises/01-terraform-proxy
terraform init
terraform plan -var-file=envs/dev.tfvars
terraform apply -var-file=envs/dev.tfvars
```

## Tasks

1. Review the module structure in `modules/envoy-proxy/`
2. Understand the variables: `replicas`, `proxy_port`, `admin_port`, `upstream_host`, `upstream_port`
3. Deploy to dev using `envs/dev.tfvars`
4. Verify the proxy is running: `kubectl get pods -n proxy-lab`
5. Test routing: `kubectl port-forward svc/envoy-proxy 8080:8080 -n proxy-lab` then `curl localhost:8080`
6. Modify `envs/prod.tfvars` to use 3 replicas and redeploy

## Expected Result

- Envoy proxy pod(s) running in `proxy-lab` namespace
- Requests to the proxy are forwarded to the httpbin backend
- You can switch between dev (1 replica) and prod (3 replicas) using tfvars

## Bonus

- Add a `terraform output` for the service ClusterIP
- Add a variable for `log_level` (debug/info/warn) and wire it into the Envoy config
