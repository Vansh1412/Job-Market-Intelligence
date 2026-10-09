variable "aws_region" {
  type        = string
  description = "AWS deployment region."
  default     = "us-east-1"
}

variable "environment" {
  type        = string
  description = "Environment identifier (e.g. production, staging)."
  default     = "production"
}

variable "project_name" {
  type        = string
  description = "Base project name used in resource naming conventions."
  default     = "jobintel"
}

variable "s3_bucket_name" {
  type        = string
  description = "Globally unique name for the private S3 artifact bucket."
  default     = "jobintel-frozen-artifacts-2026-prod"
}

variable "ecr_repository_name" {
  type        = string
  description = "Name for the private Amazon ECR repository."
  default     = "jobintel-backend"
}

variable "ecs_cpu" {
  type        = number
  description = "Fargate CPU units (256 = 0.25 vCPU, 512 = 0.5 vCPU, 1024 = 1 vCPU)."
  default     = 512
}

variable "ecs_memory" {
  type        = number
  description = "Fargate Memory in MB (512, 1024, 2048)."
  default     = 1024
}

variable "container_port" {
  type        = number
  description = "Port exposed by the FastAPI container inside the task."
  default     = 8000
}

variable "app_count" {
  type        = number
  description = "Desired number of ECS task instances running simultaneously."
  default     = 1
}

variable "github_org" {
  type        = string
  description = "GitHub organization or username owning the repository."
  default     = "Vansh1412"
}

variable "github_repo" {
  type        = string
  description = "GitHub repository name."
  default     = "Job-Market-Intelligence"
}

variable "github_branch" {
  type        = string
  description = "Target GitHub branch authorized to trigger production deployments."
  default     = "master"
}

variable "github_environment" {
  type        = string
  description = "Protected GitHub Actions Environment requiring approval."
  default     = "production"
}

variable "vpc_cidr" {
  type        = string
  description = "CIDR block for the dedicated VPC."
  default     = "10.0.0.0/16"
}

variable "public_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for public subnets (ALB)."
  default     = ["10.0.1.0/24", "10.0.2.0/24"]
}

variable "private_subnet_cidrs" {
  type        = list(string)
  description = "CIDR blocks for private subnets (ECS tasks)."
  default     = ["10.0.11.0/24", "10.0.12.0/24"]
}

variable "domain_name" {
  type        = string
  description = "Custom domain name for backend API (optional, leave empty if using ALB DNS)."
  default     = ""
}

variable "certificate_arn" {
  type        = string
  description = "ACM Certificate ARN for HTTPS listener (optional, leave empty if TLS terminated elsewhere or during initial bootstrap)."
  default     = ""
}

variable "frontend_cors_origin" {
  type        = string
  description = "Allowed frontend origin URL for CORS (e.g. https://jobintel.vercel.app)."
  default     = "http://localhost:5173,http://localhost:3000"
}

variable "log_retention_days" {
  type        = number
  description = "CloudWatch log retention in days."
  default     = 14
}
