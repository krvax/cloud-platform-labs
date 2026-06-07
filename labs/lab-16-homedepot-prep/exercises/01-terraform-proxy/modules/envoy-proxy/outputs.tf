output "service_cluster_ip" {
  description = "ClusterIP assigned to the Envoy proxy service"
  value       = kubernetes_service.envoy.spec[0].cluster_ip
}
