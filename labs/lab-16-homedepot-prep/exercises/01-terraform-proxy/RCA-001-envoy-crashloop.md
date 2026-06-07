# RCA-001: Envoy CrashLoopBackOff — Invalid bootstrap_extensions

> Date: 28 Mayo 2026
> Lab: lab-16-homedepot-prep / exercise 01-terraform-proxy
> Severity: P3 (lab environment, no production impact)
> Time to resolve: ~15 min

---

## Incident Summary

After `terraform apply`, the Envoy proxy pod entered CrashLoopBackOff while httpbin backend was healthy.

## Timeline

| Time | Event |
|------|-------|
| 14:00 | `terraform apply -var-file=envs/dev.tfvars` executed |
| 14:01 | Namespace, services, configmap created successfully |
| 14:01 | httpbin deployment: Running ✅ |
| 14:01 | envoy-proxy deployment: Creating... (pulling image) |
| 14:05 | envoy-proxy: CrashLoopBackOff (5 restarts) |
| 14:06 | `kubectl logs` reveals config parse error |
| 14:10 | Root cause identified: invalid `bootstrap_extensions` type |
| 14:12 | Fix applied to `envoy.yaml.tpl` |
| 14:15 | `terraform destroy` + `terraform apply` — envoy Running ✅ |
| 14:16 | Verified: curl through proxy returns 200 from httpbin |

## Root Cause

The Envoy config template (`envoy.yaml.tpl`) included a `bootstrap_extensions` section referencing:

```yaml
bootstrap_extensions:
  - name: envoy.extensions.log_config.bootstrap.composite_logger
    typed_config:
      "@type": type.googleapis.com/envoy.extensions.log_config.bootstrap.composite_logger.v3.CompositeLogger
```

This type **does not exist** in `envoyproxy/envoy:v1.30-latest`. The error message:

```
INVALID_ARGUMENT: could not find @type 'type.googleapis.com/envoy.extensions.log_config.bootstrap.composite_logger.v3.CompositeLogger'
```

## Why It Happened

The config was likely generated or copied from documentation targeting a newer/unreleased Envoy version. The `CompositeLogger` extension is not compiled into the v1.30 distribution.

## Fix Applied

Removed the entire `bootstrap_extensions` block from `modules/envoy-proxy/templates/envoy.yaml.tpl`. This section is optional and not required for basic L7 proxy functionality.

## Verification

```bash
# Pod healthy
kubectl get pods -n proxy-lab
# envoy-proxy   1/1   Running

# Proxy routes correctly
kubectl run curl-test --rm -it --image=curlimages/curl --restart=Never -n proxy-lab \
  -- curl -s http://envoy-proxy:8080/get
# Returns httpbin JSON with X-Envoy-Expected-Rq-Timeout-Ms header

# Admin stats accessible
kubectl run curl-admin --rm -it --image=curlimages/curl --restart=Never -n proxy-lab \
  -- curl -s http://envoy-proxy:9901/stats | head -5
# Shows cluster metrics, circuit breaker status
```

## Lessons Learned

1. **Always validate Envoy config against the specific image version** — extensions vary between releases
2. **CrashLoopBackOff + config error = check logs first** — don't wait for timeout
3. **Envoy's error messages are clear** — the `could not find @type` tells you exactly what's wrong
4. **Keep configs minimal** — only add extensions you actually need

## Prevention

- Pin Envoy image to specific version (not `latest`)
- Add a `terraform plan` validation step that checks config syntax
- Consider using `envoy --mode validate -c /etc/envoy/envoy.yaml` as an init container
