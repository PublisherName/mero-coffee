variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-south-1"
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "mero-coffee"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["ap-south-1a", "ap-south-1b"]
}

variable "db_instance_class" {
  description = "RDS instance class"
  type        = string
  default     = "db.t3.micro"
}

variable "db_allocated_storage" {
  description = "RDS allocated storage in GB"
  type        = number
  default     = 20
}

variable "ecs_task_cpu" {
  description = "ECS task CPU units"
  type        = string
  default     = "2048"
}

variable "ecs_task_memory" {
  description = "ECS task memory in MB"
  type        = string
  default     = "4096"
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
  default     = "ghcr.io/publishername/merocoffee:develop"
}

variable "log_retention_days" {
  description = "CloudWatch log retention in days"
  type        = number
  default     = 7
}

variable "app_secrets_name" {
  description = "AWS Secrets Manager secret name for application"
  type        = string
  default     = "mero-coffee-application-secret"
}

variable "ghcr_credentials_name" {
  description = "AWS Secrets Manager secret name for GHCR credentials"
  type        = string
  default     = "ghcr-credentials"
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "ssl_policy" {
  description = "SSL policy for HTTPS listener"
  type        = string
  default     = "ELBSecurityPolicy-TLS13-1-2-2021-06"
}
