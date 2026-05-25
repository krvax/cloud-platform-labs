output "alb_dns_name" {
  value = aws_lb.this.dns_name
}

output "ecr_repository_url" {
  value = aws_ecr_repository.app.repository_url
}

output "ecs_cluster_name" {
  value = aws_ecs_cluster.this.name
}

output "ecs_service_name" {
  value = aws_ecs_service.app.name
}

output "ecs_task_family" {
  value = aws_ecs_task_definition.app.family
}

output "log_group_name" {
  value = aws_cloudwatch_log_group.ecs.name
}

output "azure_devops_role_arn" {
  description = "ARN del role que Azure DevOps asume via OIDC"
  value       = aws_iam_role.azure_devops_deploy.arn
}