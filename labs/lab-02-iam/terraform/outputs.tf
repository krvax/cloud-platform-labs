# ── Ejercicio A: EC2 Instance Profile ──
output "ec2_role_arn" {
  description = "ARN of the EC2 IAM role"
  value       = aws_iam_role.ec2_s3_reader.arn
}

output "instance_profile_name" {
  description = "Instance profile name to use in EC2 launch configs"
  value       = aws_iam_instance_profile.ec2_s3_reader.name
}

# ── Ejercicio B: AssumeRole simple ──
output "assumable_role_arn" {
  description = "ARN para practicar assume role sin ExternalId"
  value       = aws_iam_role.assumable.arn
}

output "assumable_role_cli_command" {
  description = "Comando CLI para probar assume role simple"
  value       = "aws sts assume-role --role-arn ${aws_iam_role.assumable.arn} --role-session-name lab02-test"
}

# ── Ejercicio C: AssumeRole con ExternalId ──
output "cross_role_arn" {
  description = "ARN del rol con ExternalId"
  value       = aws_iam_role.cross_role.arn
}

output "test_bucket" {
  description = "Bucket de prueba para verificar el assume role"
  value       = aws_s3_bucket.test.id
}

output "assume_role_command" {
  description = "Comandos completos para probar assume role con ExternalId"
  sensitive   = true
  value       = <<-EOT

    # 1. Asumir el rol
    CREDENTIALS=$(aws sts assume-role \
      --role-arn ${aws_iam_role.cross_role.arn} \
      --role-session-name test-session \
      --external-id ${var.external_id} \
      --query 'Credentials' \
      --output json)

    # 2. Exportar credenciales temporales
    export AWS_ACCESS_KEY_ID=$(echo $CREDENTIALS | jq -r '.AccessKeyId')
    export AWS_SECRET_ACCESS_KEY=$(echo $CREDENTIALS | jq -r '.SecretAccessKey')
    export AWS_SESSION_TOKEN=$(echo $CREDENTIALS | jq -r '.SessionToken')

    # 3. Verificar identidad
    aws sts get-caller-identity

    # 4. Probar S3 (debe funcionar ✅)
    aws s3 ls
    aws s3 cp s3://${aws_s3_bucket.test.id}/test.txt -

    # 5. Probar EC2 (debe FALLAR ❌)
    aws ec2 describe-instances

    # 6. Volver a tu identidad original
    unset AWS_ACCESS_KEY_ID AWS_SECRET_ACCESS_KEY AWS_SESSION_TOKEN
  EOT
}
