terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # In production, configure an S3 remote backend with DynamoDB locking.
  # backend "s3" {
  #   bucket         = "your-terraform-state-bucket"
  #   key            = "jobintel/production/terraform.tfstate"
  #   region         = "us-east-1"
  #   encrypt        = true
  #   dynamodb_table = "your-terraform-locks"
  # }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Project     = "JobMarketIntelligence"
      Application = "JobIntel"
      Environment = var.environment
      ManagedBy   = "Terraform"
    }
  }
}
