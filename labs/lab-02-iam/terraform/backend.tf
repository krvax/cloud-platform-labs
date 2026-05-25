# =============================================================================
# backend.tf — Remote state en S3 (bucket creado en lab-05)
# =============================================================================

terraform {
  backend "s3" {
    bucket       = "epam-prep-tf-state-577638390094"
    key          = "lab-02-iam/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true   # Terraform 1.10+ — locking nativo sin DynamoDB
  }
}
