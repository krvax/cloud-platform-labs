# 03 — Terraform & Terragrunt: Key Concepts

> Friendly companion to the Terraform labs.
> If state, modules, workspaces, or Terragrunt sound confusing, start here.

---

## Index

1. [The Big Picture: What problem does Terraform solve?](#1-the-big-picture)
2. [Basic Lifecycle](#2-basic-lifecycle)
3. [State: The Heart of Terraform](#3-state-the-heart-of-terraform)
4. [Variables, Outputs, and Locals](#4-variables-outputs-and-locals)
5. [Data Sources: Read without Creating](#5-data-sources-read-without-creating)
6. [Modules: Reusable Code](#6-modules-reusable-code)
7. [Advanced Patterns](#7-advanced-patterns)
8. [Workspaces](#8-workspaces)
9. [Terraform with AWS: Real-world Patterns](#9-terraform-with-aws-real-world-patterns)
10. [Terragrunt: DRY for Environments](#10-terragrunt-dry-for-environments)
11. [Interview Questions with Answer Key](#11-interview-questions)

---

## 1. The Big Picture

Terraform is an **Infrastructure as Code (IaC)** tool that allows you to describe AWS resources (or other providers) in `.tf` files and apply those changes in a repeatable and predictable way.

```
Your .tf code
    │
    ▼
terraform plan    ← shows what will change (without touching anything)
    │
    ▼
terraform apply   ← creates/modifies/destroys resources in AWS
    │
    ▼
terraform.tfstate ← stores the current state of infrastructure
```

**The fundamental principle**: Terraform compares your code (desired state) against the state (actual state) and calculates the diff. It only changes what is different.

---

## 2. Basic Lifecycle

```bash
# 1. Initialize: download providers and modules
terraform init

# 2. Format code (best practice before committing)
terraform fmt

# 3. Validate syntax
terraform validate

# 4. See what would change (never touches AWS)
terraform plan

# 5. Apply changes
terraform apply

# 5b. Apply without manual confirmation (for CI/CD pipelines)
terraform apply -auto-approve

# 6. Destroy everything (caution!)
terraform destroy
```

### Minimum Project Structure

```
my-project/
  main.tf          # Primary resources
  variables.tf     # Variable declarations
  outputs.tf       # Values you want to expose
  providers.tf     # Provider configuration (AWS, version, region)
  terraform.tfvars # Variable values (do not commit if it contains secrets)
```

### providers.tf — Always pin the version

```hcl
terraform {
  required_version = ">= 1.6.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"   # accepts 5.x but not 6.x
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      ManagedBy   = "terraform"
      Project     = var.project_name
    }
  }
}
```

> 💡 `default_tags` in the provider applies those tags to **all** resources automatically. It is a best practice that many are unaware of and that EPAM values.

---

## 3. State: The Heart of Terraform

### What is State?

`terraform.tfstate` is a JSON file that Terraform maintains to know which resources exist in the real world and what their current attributes are.

**Without state**: Terraform cannot know if a resource already exists or if it needs to be created.
**With corrupt or desynchronized state**: Terraform may create duplicate resources or attempt to destroy things it shouldn't.

### Remote State: Mandatory for Teams

Local state (`terraform.tfstate` on your machine) is only for personal projects. In teams, you use **remote state** in S3 + DynamoDB for locking.

```hcl
# backend.tf
terraform {
  backend "s3" {
    bucket         = "my-company-terraform-state"
    key            = "projects/eks-cluster/terraform.tfstate"
    region         = "us-east-1"
    dynamodb_table = "terraform-state-locks"
    encrypt        = true
  }
}
```

```bash
# Create the bucket and table BEFORE running terraform init
aws s3api create-bucket \
  --bucket my-company-terraform-state \
  --region us-east-1

aws s3api put-bucket-versioning \
  --bucket my-company-terraform-state \
  --versioning-configuration Status=Enabled

aws dynamodb create-table \
  --table-name terraform-state-locks \
  --attribute-definitions AttributeName=LockID,AttributeType=S \
  --key-schema AttributeName=LockID,KeyType=HASH \
  --billing-mode PAY_PER_REQUEST
```

### Why S3 + DynamoDB?

| Component | Purpose |
|---|---|
| S3 | Stores the state file |
| S3 Versioning | Allows recovery of previous state versions |
| DynamoDB | State locking — prevents two `terraform apply` runs from occurring simultaneously |
| S3 Encryption | State may contain secrets (RDS passwords, etc.) |

### State Manipulation Commands

```bash
# List all resources in the state
terraform state list

# View details of a specific resource
terraform state show aws_instance.web

# Rename a resource in the state (without destroying the real resource)
terraform state mv aws_instance.web aws_instance.web_server

# Remove a resource from the state (without destroying the real resource)
# Useful when you want Terraform to stop managing something
terraform state rm aws_s3_bucket.legacy

# Import an existing AWS resource into the state
# (for resources created manually that you want to manage with TF)
terraform import aws_s3_bucket.my-bucket my-aws-bucket-name
```

> ⚠️ `terraform state rm` + `terraform import` are the most commonly used commands when someone manually modified a resource in the AWS console and broke the state.

---

## 4. Variables, Outputs, and Locals

### Variables: Inputs for your module or project

```hcl
# variables.tf
variable "environment" {
  description = "Deployment environment"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "instance_count" {
  description = "Number of EC2 instances"
  type        = number
  default     = 2
}

variable "allowed_cidrs" {
  description = "Allowed CIDRs in the Security Group"
  type        = list(string)
  default     = ["10.0.0.0/8"]
}

variable "tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}
}
```

```hcl
# terraform.tfvars (concrete values)
environment    = "prod"
instance_count = 3
allowed_cidrs  = ["10.0.0.0/8", "172.16.0.0/12"]
```

### Outputs: Values you expose

```hcl
# outputs.tf
output "vpc_id" {
  description = "ID of the created VPC"
  value       = aws_vpc.main.id
}

output "rds_endpoint" {
  description = "Database endpoint"
  value       = aws_db_instance.main.endpoint
  sensitive   = true   # won't be shown in CI/CD logs
}
```

Module outputs are consumed like this:
```hcl
module.vpc.vpc_id
module.rds.rds_endpoint
```

### Locals: Internal variables (not inputs)

```hcl
locals {
  # Build a consistent name for all resources
  name_prefix = "${var.project}-${var.environment}"

  # Merge default tags with user tags
  common_tags = merge(
    {
      Environment = var.environment
      ManagedBy   = "terraform"
    },
    var.tags
  )

  # Calculate logic based on other variables
  is_production = var.environment == "prod"
}

# Using locals
resource "aws_vpc" "main" {
  cidr_block = var.vpc_cidr
  tags = merge(local.common_tags, {
    Name = "${local.name_prefix}-vpc"
  })
}
```

---

## 5. Data Sources: Read without Creating

A data source **reads** information from existing resources without creating them.

```hcl
# Read the latest Amazon Linux 2 AMI (without hardcoding the ID)
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}

# Read an existing VPC by tag
data "aws_vpc" "existing" {
  filter {
    name   = "tag:Name"
    values = ["my-production-vpc"]
  }
}

# Read current AWS account ID (very useful for ARNs)
data "aws_caller_identity" "current" {}

# Using data sources
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id   # always the latest AMI
  subnet_id     = data.aws_vpc.existing.id
}

output "account_id" {
  value = data.aws_caller_identity.current.account_id
}
```

---

## 6. Modules: Reusable Code

### What is a Module?

A module is simply **a directory containing `.tf` files**. Any Terraform project is technically a module (the root module). Child modules are the ones you reuse.

### Reusable Module Structure

```
modules/
  vpc/
    main.tf        # Resources (aws_vpc, aws_subnet, etc.)
    variables.tf   # Module inputs
    outputs.tf     # Exposed values
    README.md      # Documentation (mandatory for teams)
```

```hcl
# modules/vpc/variables.tf
variable "vpc_cidr"        { type = string }
variable "environment"     { type = string }
variable "azs"             { type = list(string) }
variable "public_subnets"  { type = list(string) }
variable "private_subnets" { type = list(string) }
```

```hcl
# modules/vpc/outputs.tf
output "vpc_id"          { value = aws_vpc.main.id }
output "public_subnets"  { value = aws_subnet.public[*].id }
output "private_subnets" { value = aws_subnet.private[*].id }
```

### Consuming a Module

```hcl
# envs/prod/main.tf
module "vpc" {
  source = "../../modules/vpc"   # relative path

  vpc_cidr        = "10.0.0.0/16"
  environment     = "prod"
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}

# Use module outputs in another resource
module "eks" {
  source = "../../modules/eks"

  vpc_id     = module.vpc.vpc_id          # vpc module output
  subnet_ids = module.vpc.private_subnets
}
```

### Modules from the Public Terraform Registry

```hcl
# Instead of writing from scratch, use an official module
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"   # always pin the version

  cluster_name    = "my-cluster"
  cluster_version = "1.29"
  vpc_id          = module.vpc.vpc_id
  subnet_ids      = module.vpc.private_subnets
}
```

> 💡 **How to version internal modules in a team**: Keep them in a separate Git repo and reference them by Git tag:
> ```hcl
> source = "git::https://github.com/my-company/terraform-modules.git//vpc?ref=v2.1.0"
> ```
> This allows each team to update module versions when they choose, without breaking others.

---

## 7. Advanced Patterns

### `count` vs `for_each`

```hcl
# count — useful for creating N identical copies
resource "aws_instance" "web" {
  count         = 3
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  tags = {
    Name = "web-${count.index}"   # web-0, web-1, web-2
  }
}

# Problem with count: if you remove index 1, Terraform destroys and recreates 2 and 3
# because it identifies them by position in the list.
```

```hcl
# for_each — better for resources with their own identity
locals {
  buckets = {
    logs    = { region = "us-east-1" }
    backups = { region = "us-west-2" }
    assets  = { region = "us-east-1" }
  }
}

resource "aws_s3_bucket" "this" {
  for_each = local.buckets

  bucket = "my-company-${each.key}"

  tags = {
    Name    = each.key
    Region  = each.value.region
  }
}

# Advantage: each resource is identified by a key ("logs", "backups", "assets").
# If you remove "backups", only that bucket is destroyed, not the others.
```

**Rule**: Use `for_each` almost always. Use `count` only for truly identical things where the index doesn't matter.

### `dynamic` blocks

When a block inside a resource needs to repeat a variable number of times:

```hcl
variable "ingress_rules" {
  default = [
    { port = 80,  cidr = "0.0.0.0/0" },
    { port = 443, cidr = "0.0.0.0/0" },
    { port = 8080, cidr = "10.0.0.0/8" },
  ]
}

resource "aws_security_group" "web" {
  name   = "web-sg"
  vpc_id = aws_vpc.main.id

  dynamic "ingress" {
    for_each = var.ingress_rules
    content {
      from_port   = ingress.value.port
      to_port     = ingress.value.port
      protocol    = "tcp"
      cidr_blocks = [ingress.value.cidr]
    }
  }
}
```

### `lifecycle` rules

```hcl
resource "aws_instance" "web" {
  ami           = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  lifecycle {
    # Create new resource before destroying the old one
    # Useful for resources that cannot have downtime
    create_before_destroy = true

    # Never destroy this resource (e.g., production database)
    prevent_destroy = true

    # Ignore changes in these attributes (e.g., if someone changes AMI manually)
    ignore_changes = [ami, tags["LastDeployment"]]
  }
}
```

### `templatefile()`

```hcl
# Generate user-data script dynamically
resource "aws_launch_template" "web" {
  name_prefix   = "web-"
  image_id      = data.aws_ami.amazon_linux.id
  instance_type = "t3.micro"

  user_data = base64encode(templatefile("${path.module}/templates/user-data.sh.tpl", {
    environment    = var.environment
    app_version    = var.app_version
    db_endpoint    = module.rds.endpoint
  }))
}
```

---

## 8. Workspaces

Workspaces allow you to have **multiple states** with the same code.

```bash
# View existing workspaces
terraform workspace list

# Create a new workspace
terraform workspace new staging

# Switch workspaces
terraform workspace select prod

# View current workspace
terraform workspace show
```

```hcl
# Use workspace in code
locals {
  instance_type = terraform.workspace == "prod" ? "t3.large" : "t3.micro"
  replica_count = terraform.workspace == "prod" ? 3 : 1
}
```

### Workspaces vs Separate Directories by Environment

| | Workspaces | Separate Directories |
|---|---|---|
| **Code** | Same code, different state | Code separated per environment |
| **Risk** | High: `terraform destroy` in prod is easy | Low: clear context |
| **Flexibility** | Limited | High (vastly different configs per env) |
| **Recommended for** | Very similar environments | Environments with significant differences |

> 💡 **Industry Opinion**: For real production environments, most prefer **separate directories + Terragrunt** over workspaces. Workspaces are useful for feature branches or ephemeral testing.

---

## 9. Terraform with AWS: Real-world Patterns

### Recommended Repo Organization

```
infrastructure/
  modules/
    vpc/
    eks/
    rds/
    iam/
  envs/
    dev/
      main.tf
      terraform.tfvars
      backend.tf
    staging/
      main.tf
      terraform.tfvars
      backend.tf
    prod/
      main.tf
      terraform.tfvars
      backend.tf
```

### Managing EKS with Terraform

```hcl
module "eks" {
  source  = "terraform-aws-modules/eks/aws"
  version = "~> 20.0"

  cluster_name    = "${local.name_prefix}-eks"
  cluster_version = "1.29"

  vpc_id                         = module.vpc.vpc_id
  subnet_ids                     = module.vpc.private_subnets
  cluster_endpoint_public_access = true

  # Karpenter instead of managed node groups
  # (needs a minimum node group for Karpenter to run)
  eks_managed_node_groups = {
    karpenter = {
      instance_types = ["t3.medium"]
      min_size       = 1
      max_size       = 2
      desired_size   = 1

      taints = {
        addons = {
          key    = "CriticalAddonsOnly"
          value  = "true"
          effect = "NO_SCHEDULE"
        }
      }
    }
  }

  # Cluster access
  enable_cluster_creator_admin_permissions = true
}
```

### Managing IAM with Terraform (Least Privilege)

```hcl
# Policy with least privilege for an app that only reads from S3
data "aws_iam_policy_document" "app_s3_read" {
  statement {
    effect = "Allow"
    actions = [
      "s3:GetObject",
      "s3:ListBucket",
    ]
    resources = [
      aws_s3_bucket.app_data.arn,
      "${aws_s3_bucket.app_data.arn}/*",
    ]
  }
}

resource "aws_iam_policy" "app_s3_read" {
  name   = "${local.name_prefix}-app-s3-read"
  policy = data.aws_iam_policy_document.app_s3_read.json
}
```

---

## 10. Terragrunt: DRY for Environments

### The problem it solves

With pure Terraform, when you have multiple environments, you repeat a lot of code:
- The `backend` block is almost identical in every environment (only `key` changes)
- The `provider` block is the same in all
- Module calls are the same, only some values change

Terragrunt is a **wrapper** for Terraform that eliminates this repetition.

### Structure with Terragrunt

```
infrastructure/
  terragrunt.hcl          ← Root configuration (backend, provider)
  modules/
    vpc/
    eks/
  envs/
    dev/
      terragrunt.hcl      ← Inherits from root + dev values
      vpc/
        terragrunt.hcl    ← Calls vpc module with dev values
      eks/
        terragrunt.hcl    ← Calls eks module with dev values
    prod/
      terragrunt.hcl
      vpc/
        terragrunt.hcl
      eks/
        terragrunt.hcl
```

### Root terragrunt.hcl — Dynamic Backend

```hcl
# infrastructure/terragrunt.hcl

locals {
  # Extract environment from current path
  env = basename(dirname(find_in_parent_folders()))
}

# Backend configured once for all modules
remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket         = "my-company-terraform-state"
    key            = "${path_relative_to_include()}/terraform.tfstate"
    region         = "us-east-1"
    encrypt        = true
    dynamodb_table = "terraform-state-locks"
  }
}

# Automatically generated Provider
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "aws" {
  region = "us-east-1"
  default_tags {
    tags = {
      Environment = "${local.env}"
      ManagedBy   = "terragrunt"
    }
  }
}
EOF
}
```

### Per-module terragrunt.hcl — No Repetition

```hcl
# envs/prod/vpc/terragrunt.hcl

# Inherit all root config (backend, provider)
include "root" {
  path = find_in_parent_folders()
}

# Point to Terraform module
terraform {
  source = "../../../modules/vpc"
}

# Define only environment-specific values
inputs = {
  vpc_cidr        = "10.0.0.0/16"
  environment     = "prod"
  azs             = ["us-east-1a", "us-east-1b", "us-east-1c"]
  public_subnets  = ["10.0.1.0/24", "10.0.2.0/24", "10.0.3.0/24"]
  private_subnets = ["10.0.11.0/24", "10.0.12.0/24", "10.0.13.0/24"]
}
```

```hcl
# envs/prod/eks/terragrunt.hcl

include "root" {
  path = find_in_parent_folders()
}

# Explicit dependency: EKS needs VPC to exist first
dependency "vpc" {
  config_path = "../vpc"

  # Mock values to allow plan without VPC being created
  mock_outputs = {
    vpc_id          = "vpc-00000000"
    private_subnets = ["subnet-00000000", "subnet-11111111"]
  }
}

terraform {
  source = "../../../modules/eks"
}

inputs = {
  cluster_name    = "my-company-prod"
  cluster_version = "1.29"
  vpc_id          = dependency.vpc.outputs.vpc_id
  subnet_ids      = dependency.vpc.outputs.private_subnets
}
```

### Terragrunt Commands

```bash
# Equivalent to Terraform commands
terragrunt init
terragrunt plan
terragrunt apply

# Most powerful: apply ALL modules of an environment in order
cd envs/prod
terragrunt run-all apply

# Plan everything without applying
terragrunt run-all plan

# Only modules that changed (Terragrunt detects dependencies)
terragrunt run-all apply --terragrunt-include-dir vpc
```

---

## 11. Interview Questions

**"What happens if two people run `terraform apply` at the same time?"**

```
Without remote state locking:
- Both read the same state
- Both calculate diff on the same state
- Both apply changes simultaneously
- State becomes corrupt: last writer wins, first is lost
- Result: duplicate resources, desynchronized state, chaos

With S3 + DynamoDB locking:
- First one to run apply acquires the lock in DynamoDB
- Second one sees an error: "state is locked by [user], started at [time]"
- Second one waits or cancels
- When the first finishes, it releases the lock
- Second one can proceed with the updated state
```

---

**"Someone manually modified a resource in AWS. What happens?"**

```
Terraform doesn't detect changes in real-time — only when you run plan/apply.

When you run terraform plan:
- Terraform reads the state (what it thinks exists)
- Terraform reads the actual state from AWS (API)
- Detects the difference
- Shows that it wants to "revert" the manual change

Options:
1. terraform apply → reverts the manual change (IaC wins)
2. terraform import → imports current status to state to adopt it
3. ignore_changes in lifecycle → Terraform ignores that attribute forever

Correct interview answer: "Ideally, no one should modify manually.
A policy is established: all changes go through Terraform and PR review.
To detect drift, we run terraform plan in a CI pipeline nightly."
```

---

**"How do you avoid duplicating code between environments in Terraform?"**

```
Three levels of maturity:

1. Local modules — extract common logic to modules/ and call it from each environment.
   Eliminates logic duplication but not boilerplate (backend, provider).

2. Modules + variables — use the same module with different terraform.tfvars per env.
   Works well for small teams.

3. Terragrunt — a root terragrunt.hcl defines backend and provider once.
   Each module inherits that config and defines its inputs.
   Manages dependencies between modules automatically.
   Standard for large teams with many environments.
```

---

**"What is `terraform import` and when do you use it?"**

```
terraform import associates an existing AWS resource with a Terraform resource block.
Use it when:
- Someone created infra manually and you want to manage it with TF
- Migrating from CloudFormation to Terraform
- State is corrupt and you lost track of a resource

Example:
# 1. Write the resource block in your .tf (empty is fine)
resource "aws_s3_bucket" "my-bucket" {}

# 2. Import
terraform import aws_s3_bucket.my-bucket my-aws-bucket-name

# 3. Run plan to see which attributes are missing in your code
terraform plan

# 4. Complete the code until the plan shows "No changes"

From Terraform 1.5+, there is also the import{} block in HCL, which is more declarative.
```

---

**"How do you handle secrets in Terraform?"**

```
What NOT to do:
- Hardcode passwords in .tf or .tfvars (they go to Git → leak)
- Use unencrypted environment variables in CI/CD

What TO do:

1. AWS Secrets Manager as source of truth:
   data "aws_secretsmanager_secret_version" "db_password" {
     secret_id = "prod/rds/password"
   }
   # Terraform reads secret at runtime, never saves it in code

2. State encryption:
   - State may contain sensitive values (RDS passwords, etc.)
   - Use encrypt = true in the S3 backend
   - S3 bucket must have restricted access only to the CI/CD role

3. sensitive = true in outputs:
   output "db_password" {
     value     = random_password.db.result
     sensitive = true   # doesn't appear in CI/CD logs
   }

4. In CI/CD pipelines:
   - Secrets in GitHub Actions Secrets / AWS Parameter Store
   - Never in visible environment variables in logs
```

---

**"How do you perform Kubernetes upgrades with Terraform?"**

```
EKS upgrades have a mandatory order:

1. Update control plane first (in EKS module):
   cluster_version = "1.29"  →  "1.30"
   terraform apply
   # AWS updates control plane without downtime

2. Update cluster add-ons (CoreDNS, kube-proxy, VPC CNI):
   aws eks update-addon --cluster-name my-cluster --addon-name coredns --version ...

3. Update node groups:
   # Change version in Launch Template
   # Node group performs rolling update (one node at a time)

4. Verify pods are still running:
   kubectl get pods -A

Risk: You can only jump one minor version at a time (1.28 → 1.29).
With Terraform, changing cluster_version handles step 1 automatically.
```

---

## 📖 Navigation

- **⬅️ Previous:** [02-terraform-basics.en.md](./02-terraform-basics.en.md) — Terraform Fundamentals
- **➡️ Next:** [04-cicd-concepts.en.md](./04-cicd-concepts.en.md) — CI/CD
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
