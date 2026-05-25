# Lab 12: FastAPI on ECS Fargate with Azure DevOps CI/CD

Deploy a FastAPI application to AWS ECS Fargate using Terraform for infrastructure
and Azure DevOps for the CI/CD pipeline. Implements OIDC authentication (no static
AWS credentials), native S3 state locking, and a multi-stage pipeline.

---

## 💡 Senior Interview Narrative

> [!IMPORTANT]
> This lab was built as a technical vehicle for the **PPG Senior DevOps Interview**.
> For the full strategic preparation, see: [🎯 01-TECHNICAL-PREP.md](../../MACR/interview-prep/epam/ppg/01-TECHNICAL-PREP.md)

### 1. "Why ECS Fargate instead of EKS?"
> "For this project, I chose **ECS Fargate** because of its serverless operational model. While I'm very comfortable with EKS, Fargate eliminates the overhead of managing EC2 worker nodes and patching AMIs. It's the perfect 'Day 1' solution for microservices where time-to-market and low operational burden are priorities."

### 2. "How did you handle Terraform State?"
> "I implemented **Native S3 State Locking** using `use_lockfile = true`, available since Terraform 1.10+. This eliminates the need for a DynamoDB table while maintaining strict consistency in a team environment."

### 3. "Explain your Security Strategy."
> "I used **Security Group Isolation**. The ALB is in a public SG allowing only HTTP on port 80. The ECS tasks are in a private SG that only allows traffic from the ALB's SG on port 8000. For CI/CD authentication, I implemented **OIDC** — Azure DevOps assumes an AWS IAM role via federated identity. No static credentials anywhere."

### 4. "How does the CI/CD handle new deployments?"
> "The pipeline uses a **Multi-Stage YAML** approach. First, it runs Pytests. Then it builds and pushes the Docker image to ECR using the Build ID as a tag for traceability. Finally, Terraform applies the new image tag and `force-new-deployment` triggers a zero-downtime rolling update on ECS."

### 5. "What about observability?"
> "I configured a **CloudWatch Log Group** in Terraform specifically for ECS tasks. The `awslogs` driver in the Task Definition ensures every container execution is traceable from the moment it starts."

### 6. "Why OIDC instead of Access Keys for CI/CD?"
> "Static Access Keys are a security liability — if leaked, they provide permanent access until manually rotated. With OIDC, Azure DevOps generates a short-lived JWT token signed by Microsoft. AWS IAM trusts that token via a federated Identity Provider, issues temporary credentials valid for 15 minutes, and they expire automatically. Zero rotation, zero secrets to manage."

---

## Architecture

```
Developer pushes code → GitHub (main branch)
            ↓
Azure DevOps Pipeline triggers
            ↓
    ┌─────────────────────────┐
    │  CI Stage               │
    │  - Run Pytest           │
    │  - Build Docker image   │
    │  - Login ECR via OIDC   │
    │  - Push to ECR          │
    └────────────┬────────────┘
                 ↓
    ┌─────────────────────────┐
    │  CD Stage               │
    │  - Terraform init/apply │
    │  - Force ECS deploy     │
    │  - Wait for stable      │
    │  - Show ALB URL         │
    └─────────────────────────┘
                 ↓
    ┌─────────────────────────────────────┐
    │  AWS us-east-1                      │
    │                                     │
    │  Internet → ALB (port 80)           │
    │              ↓                      │
    │  ECS Fargate Service (port 8000)    │
    │              ↓                      │
    │  ECR (image registry)               │
    │  CloudWatch Logs (/ecs/ecs-fastapi) │
    └─────────────────────────────────────┘
```

---

## OIDC Flow (How Azure DevOps authenticates to AWS)

```
Azure DevOps Pipeline runs
        ↓
Azure DevOps generates a JWT token signed by Microsoft
        ↓
AWS IAM OIDC Provider trusts vstoken.dev.azure.com/coatl-tech
        ↓
Pipeline calls AssumeRoleWithWebIdentity with the JWT
        ↓
AWS returns temporary credentials (15 min TTL)
        ↓
Pipeline uses those credentials for ECR + ECS + Terraform
```

No Access Keys. No secrets to rotate. Credentials expire automatically.

---

## Project Structure

```
labs/lab-12-ppg-ecs-azuredevops/
├── app/
│   ├── main.py            # FastAPI app (/ and /health endpoints)
│   ├── requirements.txt   # fastapi, uvicorn, pytest, httpx
│   ├── test_main.py       # Unit tests (2 tests, all passing)
│   └── Dockerfile         # Multi-stage build, port 8000
├── terraform/
│   ├── main.tf            # Provider + S3 backend
│   ├── variables.tf       # Region, project name, port, AzDO org/project
│   ├── vpc.tf             # VPC, 2 public subnets (2 AZs), IGW, route tables
│   ├── ecr.tf             # ECR repo + lifecycle policy (keep last 10 images)
│   ├── iam.tf             # ECS task execution role
│   ├── oidc.tf            # OIDC provider + Azure DevOps deploy role
│   ├── logs.tf            # CloudWatch log group (7 day retention)
│   ├── security.tf        # ALB SG (port 80) + ECS SG (port 8000 from ALB)
│   ├── alb.tf             # ALB + target group (type: ip) + listener
│   ├── ecs.tf             # ECS cluster + task definition + service
│   ├── outputs.tf         # ALB DNS, ECR URL, role ARN, cluster/service names
│   └── terraform.tfvars   # azure_devops_org, azure_devops_project
└── azure-pipelines.yml    # Multi-stage CI/CD pipeline with OIDC
```

---

## Prerequisites

### Tools
- Terraform >= 1.10 (tested with 1.15.2)
- Docker
- AWS CLI configured
- Git

### Accounts
- AWS account with admin permissions
- Azure DevOps account (dev.azure.com)
- AWS Tools for Azure DevOps extension installed

---

## Setup (First Time)

### 1. Create S3 bucket for Terraform state

```bash
aws s3 mb s3://ecs-lab-tfstate-$(aws sts get-caller-identity --query Account --output text) --region us-east-1
```

### 2. Update terraform/main.tf backend

```hcl
backend "s3" {
  bucket       = "ecs-lab-tfstate-<YOUR-ACCOUNT-ID>"
  key          = "ecs-lab/terraform.tfstate"
  region       = "us-east-1"
  use_lockfile = true
}
```

### 3. Update terraform/terraform.tfvars

```hcl
azure_devops_org     = "<your-azdo-org>"
azure_devops_project = "<your-azdo-project>"
```

### 4. Deploy infrastructure

```bash
cd terraform
terraform init
terraform plan
terraform apply
```

Take note of the outputs — you'll need them for the pipeline.

### 5. Azure DevOps Service Connection (OIDC)

1. Install **AWS Tools for Azure DevOps** from the marketplace
2. Go to Project Settings → Service connections → New service connection → AWS
3. Check **"Use OIDC"**
4. Role to Assume: use the `azure_devops_role_arn` from Terraform output
5. Name it: `aws-oidc-ecs-lab`
6. Grant access to all pipelines

### 6. Create the pipeline

1. Pipelines → New pipeline → GitHub → your repo
2. Select **"Existing Azure Pipelines YAML file"**
3. Branch: `main`, Path: `labs/lab-12-ppg-ecs-azuredevops/azure-pipelines.yml`

> **Note:** Azure DevOps free tier requires requesting a parallelism grant.
> Fill out: https://aka.ms/azpipelines-parallelism-request (2-3 business days)
> Alternative: run a self-hosted agent on your local machine.

---

## Manual Build & Push (Before Pipeline is Ready)

Run from the `app/` directory:

```bash
# Login to ECR
aws ecr get-login-password --region us-east-1 \
  | docker login --username AWS --password-stdin \
  $(aws sts get-caller-identity --query Account --output text).dkr.ecr.us-east-1.amazonaws.com

# Build
docker build -t $(cd ../terraform && terraform output -raw ecr_repository_url):latest .

# Push
docker push $(cd ../terraform && terraform output -raw ecr_repository_url):latest

# Force ECS to pull new image
aws ecs update-service \
  --cluster ecs-fastapi-lab-cluster \
  --service ecs-fastapi-lab-service \
  --force-new-deployment \
  --region us-east-1
```

---

## Verification

```bash
curl http://ecs-fastapi-lab-alb-2097760871.us-east-1.elb.amazonaws.com/
# {"message": "Hello from ECS Fargate"}

curl http://ecs-fastapi-lab-alb-2097760871.us-east-1.elb.amazonaws.com/health
# {"status": "healthy"}
```

---

## Deployment Outputs (This Lab Instance)

```
ALB:      ecs-fastapi-lab-alb-2097760871.us-east-1.elb.amazonaws.com
ECR:      577638390094.dkr.ecr.us-east-1.amazonaws.com/ecs-fastapi-lab-repo
ROLE ARN: arn:aws:iam::577638390094:role/ecs-fastapi-lab-azure-devops-role
Cluster:  ecs-fastapi-lab-cluster
Service:  ecs-fastapi-lab-service
Logs:     /ecs/ecs-fastapi-lab
```

---

## Resources Created (23 total)

| Resource | Name | Purpose |
|---|---|---|
| VPC | ecs-fastapi-lab-vpc | Network isolation |
| Subnet A | ecs-fastapi-lab-public-a | us-east-1a |
| Subnet B | ecs-fastapi-lab-public-b | us-east-1b |
| Internet Gateway | ecs-fastapi-lab-igw | Public internet access |
| Route Table | ecs-fastapi-lab-public-rt | Routes 0.0.0.0/0 → IGW |
| Security Group | ecs-fastapi-lab-alb-sg | Port 80 from internet |
| Security Group | ecs-fastapi-lab-ecs-sg | Port 8000 from ALB only |
| ALB | ecs-fastapi-lab-alb | Layer 7 load balancer |
| Target Group | ecs-fastapi-lab-tg | type=ip, /health check |
| ALB Listener | - | Port 80 → target group |
| ECR Repository | ecs-fastapi-lab-repo | Docker image registry |
| ECR Lifecycle Policy | - | Keep last 10 images |
| CloudWatch Log Group | /ecs/ecs-fastapi-lab | Container logs, 7d retention |
| IAM Role | ecs-fastapi-lab-ecs-task-execution-role | ECS pulls ECR, writes logs |
| IAM Policy Attachment | AmazonECSTaskExecutionRolePolicy | Managed policy |
| OIDC Provider | vstoken.dev.azure.com/coatl-tech | Trusts Azure DevOps JWTs |
| IAM Role | ecs-fastapi-lab-azure-devops-role | Assumed by pipeline via OIDC |
| IAM Role Policy | ecs-fastapi-lab-azure-devops-policy | ECR push + ECS deploy |
| ECS Cluster | ecs-fastapi-lab-cluster | Fargate compute |
| ECS Task Definition | ecs-fastapi-lab-task | 256 CPU / 512 MB |
| ECS Service | ecs-fastapi-lab-service | 1 replica, rolling deploy |
| S3 Bucket | ecs-lab-tfstate-577638390094 | Terraform remote state |

---

## Cleanup (Destroy Everything)

```bash
# 1. Destroy all AWS resources
cd terraform
terraform destroy

# 2. Delete S3 bucket (must be empty first)
aws s3 rm s3://ecs-lab-tfstate-577638390094 --recursive
aws s3 rb s3://ecs-lab-tfstate-577638390094

# 3. Delete ECR images (optional — terraform destroy removes the repo)
aws ecr batch-delete-image \
  --repository-name ecs-fastapi-lab-repo \
  --image-ids imageTag=latest \
  --region us-east-1
```

> **Important:** Run `terraform destroy` before deleting the S3 bucket,
> otherwise Terraform loses its state and can't clean up resources.

---

## Troubleshooting

### "Target group is unhealthy"
```bash
# Check ECS task logs
aws logs tail /ecs/ecs-fastapi-lab --follow

# Verify app listens on 0.0.0.0:8000 (not 127.0.0.1)
# Check security group allows ALB SG → ECS on port 8000
# Verify /health returns HTTP 200
```

### "ECR image pull failed"
```bash
# Verify image exists
aws ecr describe-images --repository-name ecs-fastapi-lab-repo

# Check execution role has ECR permissions
# Verify image tag matches task definition
```

### "No hosted parallelism" in Azure DevOps
Request free grant: https://aka.ms/azpipelines-parallelism-request
Or use a self-hosted agent:
```bash
mkdir azagent && cd azagent
curl -O https://vstsagentpackage.azureedge.net/agent/3.236.1/vsts-agent-linux-x64-3.236.1.tar.gz
tar zxvf vsts-agent-linux-x64-3.236.1.tar.gz
./config.sh  # point to dev.azure.com/coatl-tech, project: ecs-azuredevops-lab
./run.sh
```
Then change `pool` in azure-pipelines.yml:
```yaml
pool:
  name: Default
```

### "Terraform state lock timeout"
```bash
# List lock files in S3
aws s3 ls s3://ecs-lab-tfstate-577638390094/

# Delete lock file manually
aws s3 rm s3://ecs-lab-tfstate-577638390094/ecs-fastapi-lab/terraform.tfstate.tflock
```

---

## Cost Estimate

| Resource | Cost/hour |
|---|---|
| ECS Fargate (0.25 vCPU / 0.5 GB) | ~$0.012 |
| ALB | ~$0.008 |
| ECR, CloudWatch, VPC | ~$0.00 |
| **Total** | **~$0.02/hr** |

Full lab running a few hours: **< $0.10 USD**
Run `terraform destroy` when done.

---

## Key Concepts Practiced

| Concept | Implementation |
|---|---|
| Serverless containers | ECS Fargate — no node management |
| Private image registry | ECR with scan_on_push + lifecycle policy |
| Layer 7 load balancing | ALB with /health check, target type: ip |
| IaC | Terraform 1.15.2, S3 backend, native lockfile |
| Keyless CI/CD auth | OIDC — Azure DevOps → AWS IAM |
| Multi-stage pipeline | CI (test+build+push) → CD (tf apply+deploy) |
| Observability | CloudWatch Logs via awslogs driver |
| Network isolation | ALB SG + ECS SG (no direct internet to containers) |

---

## Pipeline Status

| Stage | Status |
|---|---|
| Terraform apply (23 resources) | ✅ Complete |
| Docker build + ECR push (manual) | ✅ Complete |
| ECS service running + ALB healthy | ✅ Complete |
| Azure DevOps pipeline (automated) | ⏳ Pending parallelism grant |

---

## References

- [AWS ECS Fargate Docs](https://docs.aws.amazon.com/AmazonECS/latest/developerguide/launch_types.html)
- [Terraform AWS Provider](https://registry.terraform.io/providers/hashicorp/aws/latest/docs)
- [Azure DevOps YAML Schema](https://learn.microsoft.com/en-us/azure/devops/pipelines/yaml-schema/)
- [AWS Tools for Azure DevOps](https://marketplace.visualstudio.com/items?itemName=AmazonWebServices.aws-vsts-tools)
- [FastAPI Docs](https://fastapi.tiangolo.com/)