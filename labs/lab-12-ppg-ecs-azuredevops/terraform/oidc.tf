# Identity Provider — AWS confía en Azure DevOps
resource "aws_iam_openid_connect_provider" "azure_devops" {
  url = "https://vstoken.dev.azure.com/${var.azure_devops_org}"

  client_id_list = [
    "api://AzureADTokenExchange"
  ]

  thumbprint_list = [
    "626d44e704d1ceabe3bf0d53397464ac8080142c"
  ]
}

# Role que Azure DevOps va a asumir
resource "aws_iam_role" "azure_devops_deploy" {
  name = "${var.project_name}-azure-devops-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect = "Allow"
      Principal = {
        Federated = aws_iam_openid_connect_provider.azure_devops.arn
      }
      Action = "sts:AssumeRoleWithWebIdentity"
      Condition = {
        StringLike = {
          "vstoken.dev.azure.com/${var.azure_devops_org}:sub" = "sc://${var.azure_devops_org}/${var.azure_devops_project}/*"
        }
      }
    }]
  })
}

# Permisos del role — solo lo que el pipeline necesita
resource "aws_iam_role_policy" "azure_devops_deploy" {
  name = "${var.project_name}-azure-devops-policy"
  role = aws_iam_role.azure_devops_deploy.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        # Push imágenes a ECR
        Effect = "Allow"
        Action = [
          "ecr:GetAuthorizationToken",
          "ecr:BatchCheckLayerAvailability",
          "ecr:InitiateLayerUpload",
          "ecr:UploadLayerPart",
          "ecr:CompleteLayerUpload",
          "ecr:PutImage"
        ]
        Resource = "*"
      },
      {
        # Actualizar ECS service
        Effect = "Allow"
        Action = [
          "ecs:RegisterTaskDefinition",
          "ecs:UpdateService",
          "ecs:DescribeServices",
          "ecs:DescribeTaskDefinition"
        ]
        Resource = "*"
      },
      {
        # Pasar el execution role a ECS
        Effect = "Allow"
        Action = "iam:PassRole"
        Resource = aws_iam_role.ecs_task_execution_role.arn
      }
    ]
  })
}
