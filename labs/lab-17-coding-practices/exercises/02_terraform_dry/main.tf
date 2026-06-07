# Lab 17 — Ejercicio 02: Terraform DRY
#
# Principios:
# - DRY: Un solo módulo, parametrizado por ambiente
# - 12-Factor #10 (Dev/Prod Parity): Misma infra, distintos valores
# - SRP: Módulo hace UNA cosa (deploy app), root solo orquesta

terraform {
  required_version = ">= 1.5"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.region
}

# --- Variables (config externalizada, no hardcoded) ---

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "instance_count" {
  description = "Number of app instances"
  type        = number
  default     = 1
}

variable "instance_type" {
  description = "EC2 instance type"
  type        = string
  default     = "t3.micro"
}

variable "enable_monitoring" {
  description = "Enable detailed monitoring"
  type        = bool
  default     = false
}

# --- Module call (DRY: un módulo, múltiples ambientes via tfvars) ---

module "app" {
  source = "./modules/app"

  environment       = var.environment
  instance_count    = var.instance_count
  instance_type     = var.instance_type
  enable_monitoring = var.enable_monitoring

  tags = {
    Environment = var.environment
    ManagedBy   = "terraform"
    Project     = "lab-17-coding-practices"
  }
}

# --- Outputs ---

output "app_instance_ids" {
  description = "IDs of deployed instances"
  value       = module.app.instance_ids
}

output "app_public_ips" {
  description = "Public IPs (if applicable)"
  value       = module.app.public_ips
}
