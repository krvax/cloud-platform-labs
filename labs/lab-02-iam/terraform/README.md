# Lab 02 — IAM Roles con Terraform

## Archivos

```
terraform/
├── variables.tf
├── main.tf
├── outputs.tf
└── README.md
```

## Recursos que crea

**Ejercicio A — EC2 Instance Profile**
- `aws_iam_role.ec2_s3_reader` — rol para EC2 con S3 read-only (sin claves estáticas)
- `aws_iam_instance_profile` — para asociar el rol a instancias EC2
- SSM policy attachment — acceso sin SSH

**Ejercicio B — AssumeRole simple (same-account)**
- `aws_iam_role.assumable` — rol que cualquier principal de la cuenta puede asumir
- S3ReadOnlyAccess policy attachment

**Ejercicio C — AssumeRole con ExternalId**
- `aws_iam_role.cross_role` — rol con ExternalId en la Trust Policy
- Inline policy: S3 read en buckets `lab-02-test-*`
- S3 bucket de prueba con objeto de verificación

## Ejecutar

```bash
cd labs/lab-02-iam/terraform

terraform init
terraform plan
terraform apply

# Ver comandos para probar assume role con ExternalId (output sensible)
terraform output -raw assume_role_command

# Limpiar
terraform destroy
```

## Variables

| Variable | Default | Descripción |
|----------|---------|-------------|
| `aws_region` | `us-east-1` | Región AWS |
| `project_name` | `lab-02` | Prefijo para nombres de recursos |
| `s3_bucket_name` | `my-lab-bucket-replace-me` | Bucket al que EC2 puede leer |
| `external_id` | `lab-external-id-12345` | ExternalId para assume role |
| `common_tags` | `{...}` | Tags aplicados a todos los recursos |

## Qué verifica el lab

```bash
# ✅ Debe funcionar (permisos S3)
aws s3 ls
aws s3 cp s3://<bucket>/test.txt -

# ❌ Debe fallar (sin permisos EC2)
aws ec2 describe-instances
# Error: UnauthorizedOperation
```

## Preguntas de entrevista

> "¿Por qué usar un Instance Profile en vez de claves de acceso en EC2?"

Las claves estáticas en EC2 son un riesgo — si alguien accede a la instancia las obtiene. Un Instance Profile entrega credenciales temporales rotadas automáticamente vía el metadata service (`169.254.169.254`).

> "¿Qué es el ExternalId en assume role?"

Previene el *confused deputy attack* — situación donde un tercero podría asumir un rol en tu cuenta usando sus propios permisos. El ExternalId actúa como secreto compartido entre tú y quien asume el rol.

---

> 🏷️ Tags: `terraform` `iam` `assume-role` `instance-profile` `least-privilege` `s3`

---

## Documentación relacionada

- [Lab 05 — Remote State](../../lab-05-remote-state/Readme.md) — configura el bucket S3 para guardar el state de este lab remotamente
