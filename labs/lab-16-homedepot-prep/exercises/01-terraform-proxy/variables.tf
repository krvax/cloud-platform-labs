variable "namespace" {
  description = "Kubernetes namespace for the proxy"
  type        = string
  default     = "proxy-lab"
}

variable "replicas" {
  description = "Number of proxy replicas"
  type        = number
  default     = 1
}

variable "proxy_port" {
  description = "Port where Envoy listens for traffic"
  type        = number
  default     = 8080
}

variable "admin_port" {
  description = "Port for Envoy admin interface (metrics, health)"
  type        = number
  default     = 9901
}

variable "upstream_host" {
  description = "Backend service hostname"
  type        = string
  default     = "httpbin.proxy-lab.svc.cluster.local"
}

variable "upstream_port" {
  description = "Backend service port"
  type        = number
  default     = 80
}

variable "log_level" {
  description = "Envoy log level (trace, debug, info, warning, error, critical)"
  type        = string
  default     = "info"

  validation {
    condition     = contains(["trace", "debug", "info", "warning", "error", "critical"], var.log_level)
    error_message = "log_level must be one of: trace, debug, info, warning, error, critical"
  }
}
