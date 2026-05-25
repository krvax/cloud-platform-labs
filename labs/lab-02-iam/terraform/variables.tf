variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Project prefix for resource names"
  type        = string
  default     = "lab-02"
}

variable "s3_bucket_name" {
  description = "Name of the S3 bucket the EC2 role can read from"
  type        = string
  default     = "my-lab-bucket-replace-me"
}

variable "external_id" {
  description = "External ID para assume role — previene confused deputy attack"
  type        = string
  default     = "lab-external-id-12345"
  sensitive   = true
}

variable "common_tags" {
  description = "Tags applied to all resources"
  type        = map(string)
  default = {
    Project     = "epam-aws-devops-prep"
    Lab         = "lab-02-iam"
    Environment = "lab"
    ManagedBy   = "terraform"
  }
}
