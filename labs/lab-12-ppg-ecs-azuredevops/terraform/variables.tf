variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project name prefix"
  type        = string
  default     = "ecs-fastapi-lab"
}

variable "container_port" {
  description = "Container port"
  type        = number
  default     = 8000
}

variable "container_image" {
  description = "Container image to deploy"
  type        = string
  default     = ""
}

variable "azure_devops_org" {
  description = "Azure DevOps organization name"
  type        = string
}

variable "azure_devops_project" {
  description = "Azure DevOps project name"
  type        = string
}