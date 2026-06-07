variable "namespace" {
  type = string
}

variable "replicas" {
  type = number
}

variable "proxy_port" {
  type = number
}

variable "admin_port" {
  type = number
}

variable "upstream_host" {
  type = string
}

variable "upstream_port" {
  type = number
}

variable "log_level" {
  type = string
}
