# Lab 05 — Terraform Remote State

**Bloque:** 3 — Infraestructura como Código (Terraform)

**Objetivo:** Configurar un backend remoto en S3 con locking nativo (Terraform 1.10+) sin DynamoDB, y usarlo como base para todos los labs posteriores.

---

## Prerequisitos

- Terraform >= 1.10
- AWS CLI configurado (`aws configure`)
- Permisos IAM: `s3:*` sobre el bucket de estado
- Lab 01 completado (VPC) — opcional pero recomendado

---

## ¿Por qué remote state?

Cuando trabajas en equipo o con múltiples entornos, el estado local (`terraform.tfstate`) genera conflictos. El remote state resuelve tres problemas:

| Problema | Solución |
|----------|----------|
| Estado local no compartido | S3 como backend centralizado |
| Dos `apply` simultáneos corrompen el estado | Locking nativo con `use_lockfile = true` |
| No hay historial de cambios | S3 versioning habilitado |

> **Terraform 1.10+**: DynamoDB ya no es necesario para locking.
> `use_lockfile = true` crea un archivo `.tflock` directamente en S3
> usando S3 conditional writes. Sin tabla extra, sin costo adicional.

---

## Arquitectura

```
terraform apply
    │
    ├─→ S3 Bucket (state)
    │     ├── terraform.tfstate          ← estado actual
    │     ├── terraform.tfstate.tflock   ← lock file (mientras apply corre)
    │     └── versioning habilitado      ← historial de estados
    │
    └─→ IAM Policy
          └── s3:GetObject, PutObject, DeleteObject, ListBucket
```

---

## Estructura del lab

```
lab-05-remote-state/
├── Readme.md
└── terraform/
    ├── main.tf         ← crea el bucket S3 con versioning y encryption
    ├── backend.tf      ← backend remoto activo (use_lockfile = true, sin DynamoDB)
    ├── variables.tf
    └── outputs.tf      ← incluye bloque backend listo para copiar en otros labs
```

---

## Paso a paso

> **Estado actual:** bucket `epam-prep-tf-state-577638390094` ya creado y backend activo.
> Los pasos siguientes son para reproducir el proceso desde cero.

### 1. Bootstrap — aplicar con state local

El bucket de estado no puede crearse usando el mismo backend que va a guardar su propio estado. El `backend.tf` viene con el bloque comentado para este primer paso.

```bash
cd terraform/

# Verificar que backend.tf tiene el bloque terraform { backend "s3" } comentado
terraform init
terraform plan
terraform apply

# Anotar el nombre del bucket
terraform output state_bucket_name
```

### 2. Activar el backend remoto

Edita `backend.tf`, reemplaza `<YOUR_ACCOUNT_ID>` con el valor del output anterior y descomenta el bloque `terraform { backend "s3" { ... } }`:

```hcl
terraform {
  backend "s3" {
    bucket       = "epam-prep-tf-state-<YOUR_ACCOUNT_ID>"
    key          = "lab-05/terraform.tfstate"
    region       = "us-east-1"
    encrypt      = true
    use_lockfile = true
  }
}
```

### 3. Migrar el state local al bucket

```bash
terraform init -migrate-state
# Terraform pregunta: "Do you want to copy existing state to the new backend?" → yes
```

Output esperado:
```
Initializing the backend...
Successfully configured the backend "s3"!
```

### 4. Verificar el lock file en S3

```bash
# Durante un apply (en otra terminal)
aws s3 ls s3://<bucket-name>/ --recursive | grep tflock
# → terraform.tfstate.tflock  ← existe mientras el apply corre

# Después del apply
aws s3 ls s3://<bucket-name>/ --recursive
# → terraform.tfstate  ← solo queda el estado
```

### 5. Verificar versioning del estado

```bash
aws s3api list-object-versions \
  --bucket <bucket-name> \
  --prefix terraform.tfstate \
  --query 'Versions[*].{VersionId:VersionId,LastModified:LastModified}'
```

---

## Permisos IAM necesarios

A diferencia del approach antiguo con DynamoDB, ahora solo necesitas permisos S3:

```json
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:ListBucket",
        "s3:GetObject",
        "s3:PutObject",
        "s3:DeleteObject"
      ],
      "Resource": [
        "arn:aws:s3:::epam-tf-state-*",
        "arn:aws:s3:::epam-tf-state-*/*"
      ]
    }
  ]
}
```

> Ya no se necesitan permisos de DynamoDB (`dynamodb:PutItem`, `GetItem`, `DeleteItem`).

---

## Pregunta de entrevista

**"¿Qué pasa si dos personas hacen `terraform apply` al mismo tiempo sin locking?"**

Respuesta: Sin locking, ambos procesos leen el mismo estado, hacen sus cambios en paralelo, y el segundo en escribir sobreescribe los cambios del primero — corrupción de estado. Con `use_lockfile = true`, el segundo proceso falla inmediatamente con un error de lock, protegiéndose de la condición de carrera.

**"¿Por qué ya no necesitas DynamoDB para el locking en Terraform?"**

Respuesta: Desde Terraform 1.10, el backend S3 soporta locking nativo usando S3 conditional writes (`If-None-Match` header). Terraform crea un archivo `.tflock` en el mismo bucket antes de operar y lo elimina al terminar. Si otro proceso intenta crear ese archivo mientras existe, S3 rechaza la operación — sin necesidad de una tabla externa.

---

## Cleanup

```bash
terraform destroy

# El bucket de estado NO se destruye con terraform destroy
# (tiene prevent_destroy). Eliminarlo manualmente si es necesario:
aws s3 rm s3://<bucket-name> --recursive
aws s3api delete-bucket --bucket <bucket-name>
```

---

## Documentación relacionada

- [Terraform S3 Backend — Docs oficiales](https://developer.hashicorp.com/terraform/language/backend/s3)
- [Lab 03 — ASG + ALB](../lab-03-asg-alb/Readme.md)
- [Lab 06 — GitLab CI/CD](../lab-06-gitlab-cicd/Readme.md)
