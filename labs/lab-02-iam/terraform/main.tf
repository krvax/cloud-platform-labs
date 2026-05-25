terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = { source = "hashicorp/aws", version = "~> 5.0" }
  }
}

provider "aws" {
  region = var.aws_region
  default_tags {
    tags = var.common_tags
  }
}

# ============================================
# DATA
# ============================================
data "aws_caller_identity" "current" {}

# ============================================
# EJERCICIO A: EC2 Instance Profile
# Rol para que EC2 acceda a S3 sin claves estáticas
# ============================================
resource "aws_iam_role" "ec2_s3_reader" {
  name        = "${var.project_name}-ec2-s3-reader"
  description = "Allows EC2 instances to read from S3 - no static keys needed"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid       = "AllowEC2AssumeRole"
      Effect    = "Allow"
      Principal = { Service = "ec2.amazonaws.com" }
      Action    = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy" "s3_read" {
  name = "${var.project_name}-s3-read-specific-bucket"
  role = aws_iam_role.ec2_s3_reader.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListBuckets"
        Effect   = "Allow"
        Action   = ["s3:ListAllMyBuckets", "s3:GetBucketLocation"]
        Resource = "*"
      },
      {
        Sid    = "ReadSpecificBucket"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::${var.s3_bucket_name}",
          "arn:aws:s3:::${var.s3_bucket_name}/*"
        ]
      }
    ]
  })
}

# Instance Profile (necesario para asociar el role a EC2)
resource "aws_iam_instance_profile" "ec2_s3_reader" {
  name = "${var.project_name}-ec2-s3-reader-profile"
  role = aws_iam_role.ec2_s3_reader.name
}

# SSM para acceder sin SSH
resource "aws_iam_role_policy_attachment" "ssm" {
  role       = aws_iam_role.ec2_s3_reader.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonSSMManagedInstanceCore"
}

# ============================================
# EJERCICIO B: AssumeRole desde CLI (same-account)
# Rol para practicar sts:AssumeRole sin cross-account
# ============================================
resource "aws_iam_role" "assumable" {
  name                 = "${var.project_name}-assumable-role"
  description          = "Role for practicing sts:AssumeRole from CLI"
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Sid    = "AllowSameAccountAssume"
      Effect = "Allow"
      Principal = {
        AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root"
      }
      Action = "sts:AssumeRole"
    }]
  })
}

resource "aws_iam_role_policy_attachment" "assumable_s3" {
  role       = aws_iam_role.assumable.name
  policy_arn = "arn:aws:iam::aws:policy/AmazonS3ReadOnlyAccess"
}

# ============================================
# EJERCICIO C: AssumeRole con ExternalId
# Previene confused deputy attack
# ============================================
resource "aws_iam_role" "cross_role" {
  name                 = "${var.project_name}-cross-role"
  max_session_duration = 3600

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = "arn:aws:iam::${data.aws_caller_identity.current.account_id}:root" }
      Action    = "sts:AssumeRole"
      Condition = {
        StringEquals = { "sts:ExternalId" = var.external_id }
      }
    }]
  })

  tags = { Name = "${var.project_name}-cross-role" }
}

resource "aws_iam_role_policy" "s3_readonly" {
  name = "${var.project_name}-s3-readonly"
  role = aws_iam_role.cross_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid      = "ListBuckets"
        Effect   = "Allow"
        Action   = ["s3:ListAllMyBuckets", "s3:GetBucketLocation"]
        Resource = "arn:aws:s3:::*"
      },
      {
        Sid    = "ReadSpecificBuckets"
        Effect = "Allow"
        Action = ["s3:GetObject", "s3:ListBucket"]
        Resource = [
          "arn:aws:s3:::${var.project_name}-test-*",
          "arn:aws:s3:::${var.project_name}-test-*/*"
        ]
      }
    ]
  })
}

# ============================================
# S3 BUCKET DE PRUEBA (para verificar cross_role)
# ============================================
resource "aws_s3_bucket" "test" {
  bucket = "${var.project_name}-test-${data.aws_caller_identity.current.account_id}"
  tags   = { Name = "${var.project_name}-test-bucket" }
}

resource "aws_s3_object" "test_file" {
  bucket  = aws_s3_bucket.test.id
  key     = "test.txt"
  content = "Si puedes leer esto, el assume role funcionó correctamente ✅"
}
