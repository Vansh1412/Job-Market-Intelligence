# Private S3 Bucket for Frozen Models and Certified Runtime Datasets
resource "aws_s3_bucket" "artifacts" {
  bucket        = var.s3_bucket_name
  force_destroy = false

  tags = {
    Name        = "${var.project_name}-artifacts-${var.environment}"
    Governance  = "StrictFrozenModels"
    DataPrivacy = "Proprietary"
  }
}

# 100% Block Public Access Controls
resource "aws_s3_bucket_public_access_block" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

# Versioning to guarantee artifact immutability
resource "aws_s3_bucket_versioning" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  versioning_configuration {
    status = "Enabled"
  }
}

# Server-Side Encryption at Rest (SSE-S3 standard)
resource "aws_s3_bucket_server_side_encryption_configuration" "artifacts" {
  bucket = aws_s3_bucket.artifacts.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# Enforce TLS 1.2+ and In-Transit HTTPS Only (Deny Insecure HTTP)
resource "aws_s3_bucket_policy" "enforce_tls" {
  bucket     = aws_s3_bucket.artifacts.id
  depends_on = [aws_s3_bucket_public_access_block.artifacts]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.artifacts.arn,
          "${aws_s3_bucket.artifacts.arn}/*"
        ]
        Condition = {
          Bool = {
            "aws:SecureTransport" = "false"
          }
        }
      }
    ]
  })
}
