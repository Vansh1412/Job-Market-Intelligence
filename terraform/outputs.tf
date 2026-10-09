# Terraform Outputs (Secret-Free)

output "s3_bucket_name" {
  description = "Name of the private S3 bucket holding frozen artifacts."
  value       = aws_s3_bucket.artifacts.id
}

output "s3_bucket_arn" {
  description = "ARN of the private S3 bucket holding frozen artifacts."
  value       = aws_s3_bucket.artifacts.arn
}

output "ecr_repository_url" {
  description = "URL of the private ECR repository for backend container images."
  value       = aws_ecr_repository.app.repository_url
}

output "alb_dns_name" {
  description = "Public DNS name of the Application Load Balancer."
  value       = aws_lb.main.dns_name
}

output "ecs_cluster_name" {
  description = "Name of the ECS Fargate cluster."
  value       = aws_ecs_cluster.main.name
}

output "ecs_service_name" {
  description = "Name of the ECS Fargate service."
  value       = aws_ecs_service.app.name
}

output "github_actions_role_arn" {
  description = "ARN of the IAM role assumed by GitHub Actions via OIDC."
  value       = aws_iam_role.github_deploy.arn
}
