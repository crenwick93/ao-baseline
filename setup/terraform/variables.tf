variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "eu-west-1"
}

variable "instance_type" {
  description = "EC2 instance type. Use t3.medium or larger if running containers (Splunk, Vault, etc.) alongside the demo app — t3.small (2GB) is not enough."
  type        = string
  default     = "t3.small"
}

variable "allowed_cidr" {
  description = "CIDR block allowed to reach the instance (SSH, HTTP, etc.)"
  type        = string
  default     = "0.0.0.0/0"
}
