# Module: app
# SRP: Este módulo SOLO despliega la app. No hace networking, no hace DNS.

variable "environment" {
  type = string
}

variable "instance_count" {
  type    = number
  default = 1
}

variable "instance_type" {
  type    = string
  default = "t3.micro"
}

variable "enable_monitoring" {
  type    = bool
  default = false
}

variable "tags" {
  type    = map(string)
  default = {}
}

# Data source — latest Amazon Linux 2023
data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "app" {
  count = var.instance_count

  ami           = data.aws_ami.amazon_linux.id
  instance_type = var.instance_type
  monitoring    = var.enable_monitoring

  tags = merge(var.tags, {
    Name = "${var.environment}-app-${count.index + 1}"
  })

  lifecycle {
    create_before_destroy = true
  }
}

output "instance_ids" {
  value = aws_instance.app[*].id
}

output "public_ips" {
  value = aws_instance.app[*].public_ip
}
