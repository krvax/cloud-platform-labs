terraform {
  required_version = ">= 1.5.0"

  required_providers {
    kubernetes = {
      source  = "hashicorp/kubernetes"
      version = "~> 2.25"
    }
  }
}

provider "kubernetes" {
  config_path = "~/.kube/config"
}

module "envoy_proxy" {
  source = "./modules/envoy-proxy"

  namespace     = var.namespace
  replicas      = var.replicas
  proxy_port    = var.proxy_port
  admin_port    = var.admin_port
  upstream_host = var.upstream_host
  upstream_port = var.upstream_port
  log_level     = var.log_level
}
