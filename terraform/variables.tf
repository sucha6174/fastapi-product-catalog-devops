variable "aws_region" {
  description = "Target AWS region for deploying infrastructure"
  type        = string
  default     = "us-east-1"
}

variable "project_name" {
  description = "Base project name used in resource naming and tags"
  type        = string
  default     = "fastapi-product-catalog"
}

variable "environment" {
  description = "Target deployment environment (e.g., prod, dev, staging)"
  type        = string
  default     = "prod"
}

variable "vpc_cidr" {
  description = "IPv4 CIDR block for the Virtual Private Cloud"
  type        = string
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  description = "CIDR blocks for public subnets across distinct Availability Zones"
  type        = list(string)
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "availability_zones" {
  description = "AWS Availability Zones for multi-AZ high availability"
  type        = list(string)
  default     = ["us-east-1a", "us-east-1b"]
}

variable "db_name" {
  description = "PostgreSQL initial database name"
  type        = string
  default     = "product_catalog"
}

variable "db_username" {
  description = "Master username for PostgreSQL RDS instance"
  type        = string
  default     = "catalogadmin"
}

variable "db_password" {
  description = "Master password for PostgreSQL RDS instance"
  type        = string
  sensitive   = true
  default     = "CatalogSecurePass2026!"
}

variable "container_port" {
  description = "Port exposed by the FastAPI container"
  type        = number
  default     = 8000
}

variable "ecs_cpu" {
  description = "CPU units allocated for the ECS Fargate task (256 = 0.25 vCPU)"
  type        = string
  default     = "256"
}

variable "ecs_memory" {
  description = "Memory allocated for the ECS Fargate task in MB (512 = 0.5 GB)"
  type        = string
  default     = "512"
}

variable "github_repo" {
  description = "GitHub repository path in format owner/repo for OIDC role trust policy"
  type        = string
  default     = "sucha6174/fastapi-product-catalog-devops"
}

variable "enable_github_oidc" {
  description = "Whether to provision the GitHub Actions OIDC IAM role in AWS"
  type        = bool
  default     = false
}

variable "oidc_role_name" {
  description = "IAM Role Name for GitHub Actions OIDC"
  type        = string
  default     = "github-actions-fastapi-role"
}
