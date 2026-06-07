output "proxy_service_ip" {
  description = "ClusterIP of the Envoy proxy service"
  value       = module.envoy_proxy.service_cluster_ip
}

output "proxy_namespace" {
  description = "Namespace where the proxy is deployed"
  value       = var.namespace
}

output "proxy_url" {
  description = "Internal URL to reach the proxy"
  value       = "http://${module.envoy_proxy.service_cluster_ip}:${var.proxy_port}"
}
