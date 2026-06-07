resource "kubernetes_namespace" "proxy" {
  metadata {
    name = var.namespace
  }
}

# Backend service (httpbin) for the proxy to forward to
resource "kubernetes_deployment" "httpbin" {
  metadata {
    name      = "httpbin"
    namespace = kubernetes_namespace.proxy.metadata[0].name
  }

  spec {
    replicas = 1

    selector {
      match_labels = { app = "httpbin" }
    }

    template {
      metadata {
        labels = { app = "httpbin" }
      }

      spec {
        container {
          name  = "httpbin"
          image = "kennethreitz/httpbin:latest"

          port {
            container_port = 80
          }
        }
      }
    }
  }
}

resource "kubernetes_service" "httpbin" {
  metadata {
    name      = "httpbin"
    namespace = kubernetes_namespace.proxy.metadata[0].name
  }

  spec {
    selector = { app = "httpbin" }

    port {
      port        = 80
      target_port = 80
    }
  }
}

# Envoy proxy ConfigMap
resource "kubernetes_config_map" "envoy_config" {
  metadata {
    name      = "envoy-config"
    namespace = kubernetes_namespace.proxy.metadata[0].name
  }

  data = {
    "envoy.yaml" = templatefile("${path.module}/templates/envoy.yaml.tpl", {
      proxy_port    = var.proxy_port
      admin_port    = var.admin_port
      upstream_host = var.upstream_host
      upstream_port = var.upstream_port
      log_level     = var.log_level
    })
  }
}

# Envoy proxy Deployment
resource "kubernetes_deployment" "envoy" {
  metadata {
    name      = "envoy-proxy"
    namespace = kubernetes_namespace.proxy.metadata[0].name
  }

  spec {
    replicas = var.replicas

    selector {
      match_labels = { app = "envoy-proxy" }
    }

    template {
      metadata {
        labels = { app = "envoy-proxy" }
      }

      spec {
        container {
          name  = "envoy"
          image = "envoyproxy/envoy:v1.30-latest"

          port {
            name           = "proxy"
            container_port = var.proxy_port
          }

          port {
            name           = "admin"
            container_port = var.admin_port
          }

          volume_mount {
            name       = "config"
            mount_path = "/etc/envoy"
            read_only  = true
          }

          liveness_probe {
            http_get {
              path = "/ready"
              port = var.admin_port
            }
            initial_delay_seconds = 5
            period_seconds        = 10
          }

          readiness_probe {
            http_get {
              path = "/ready"
              port = var.admin_port
            }
            initial_delay_seconds = 3
            period_seconds        = 5
          }
        }

        volume {
          name = "config"

          config_map {
            name = kubernetes_config_map.envoy_config.metadata[0].name
          }
        }
      }
    }
  }
}

# Envoy proxy Service
resource "kubernetes_service" "envoy" {
  metadata {
    name      = "envoy-proxy"
    namespace = kubernetes_namespace.proxy.metadata[0].name
  }

  spec {
    selector = { app = "envoy-proxy" }

    port {
      name        = "proxy"
      port        = var.proxy_port
      target_port = var.proxy_port
    }

    port {
      name        = "admin"
      port        = var.admin_port
      target_port = var.admin_port
    }
  }
}
