# Terraform Basics — Key Concepts

## CLI vs Terraform

```text
AWS CLI                          Terraform
─────────                        ─────────
Imperative                       Declarative
"Create this, then this"         "I want this to exist"
No state management              State management (terraform.tfstate)
Hard to reproduce                100% reproducible
Cleanup: ~20 commands            terraform destroy
```

## Workflow

```text
┌──────────────┐     terraform plan      ┌─────────────┐
│  .tf files   │ ──────────────────────→ │    Plan     │
│  (your code) │                         │  (preview)  │
└──────────────┘                         └──────┬──────┘
                                                 │
                      terraform apply            │
                 ┌───────────────────────────────┘
                 ▼
        ┌──────────────┐
        │     AWS      │   Creates/modifies/deletes resources
        └──────────────┘
                 │
                 ▼
        ┌──────────────┐
        │  .tfstate    │   Stores what currently exists
        └──────────────┘
```

## Essential Commands

```bash
terraform init       # Downloads providers
terraform plan       # Preview of changes
terraform apply      # Applies changes
terraform destroy    # Destroys EVERYTHING
terraform output     # Shows output values
terraform state list # Lists resources in the state
```

## Typical Module Structure

```
lab/
├── providers.tf     ← AWS provider configuration
├── variables.tf     ← Input variables
├── main.tf          ← Core resources
├── outputs.tf       ← Output values
└── terraform.tfvars ← Variable values
```

## Key Interview Concepts

**Remote State** — Storing tfstate in S3 + DynamoDB for teamwork:
```hcl
backend "s3" {
  bucket         = "my-tfstate-bucket"
  key            = "lab/terraform.tfstate"
  region         = "us-east-1"
  dynamodb_table = "terraform-locks"
}
```

**`count` vs `for_each`** — For creating multiple resources:
```hcl
# count: when identical or a simple list
resource "aws_subnet" "public" {
  count = length(var.public_subnet_cidrs)
  cidr_block = var.public_subnet_cidrs[count.index]
}

# for_each: when unique keys are needed
resource "aws_subnet" "public" {
  for_each   = toset(var.public_subnet_cidrs)
  cidr_block = each.value
}
```

**`depends_on`** — Explicit dependencies:
```hcl
resource "aws_nat_gateway" "main" {
  depends_on = [aws_internet_gateway.main]
}
```

**`data` sources** — Read existing resources without creating them:
```hcl
data "aws_ami" "amazon_linux_2" {
  most_recent = true
  owners      = ["amazon"]
  filter {
    name   = "name"
    values = ["amzn2-ami-hvm-*-x86_64-gp2"]
  }
}
```

**`lifecycle`** — Behavior on changes:
```hcl
lifecycle {
  create_before_destroy = true  # For zero-downtime updates
  prevent_destroy       = true  # Protect critical resources
}
```

---

> 🏷️ Tags: `terraform` `iac` `aws` `state` `modules`

*To dive deeper into these concepts within an interview context: [03-terraform-concepts.en.md](03-terraform-concepts.en.md)*

---

## 📖 Navigation

- **⬅️ Previous:** [01-eks-ingress-alb.en.md](./01-eks-ingress-alb.en.md) — EKS + Ingress + ALB
- **➡️ Next:** [03-terraform-concepts.en.md](./03-terraform-concepts.en.md) — Advanced Terraform
- **🏠 Home:** [README.en.md](../README.en.md) — Documentation index
- **🔝 Back to top:** [00-concepts-overview.en.md](./00-concepts-overview.en.md) — Concept Map
