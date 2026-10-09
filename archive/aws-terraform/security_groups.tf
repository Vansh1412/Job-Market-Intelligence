# Security Groups: Strict Minimal Network Access

# ALB Security Group
resource "aws_security_group" "alb" {
  name        = "${var.project_name}-alb-sg-${var.environment}"
  description = "Controls public inbound access to the Application Load Balancer."
  vpc_id      = aws_vpc.main.id

  # Allow HTTP (port 80)
  ingress {
    description = "Allow public HTTP traffic"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Allow HTTPS (port 443)
  ingress {
    description = "Allow public HTTPS traffic"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound to ECS tasks
  egress {
    description     = "Allow outbound to ECS tasks on container port"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.ecs.id]
  }

  tags = {
    Name = "${var.project_name}-alb-sg-${var.environment}"
  }
}

# ECS Tasks Security Group
resource "aws_security_group" "ecs" {
  name        = "${var.project_name}-ecs-tasks-sg-${var.environment}"
  description = "Restricts ECS task ingress exclusively to the ALB; prevents direct internet access."
  vpc_id      = aws_vpc.main.id

  # Inbound strictly from ALB Security Group only
  ingress {
    description     = "Allow inbound traffic strictly from ALB"
    from_port       = var.container_port
    to_port         = var.container_port
    protocol        = "tcp"
    security_groups = [aws_security_group.alb.id]
  }

  # Outbound HTTPS for ECR image pull, CloudWatch logs, and S3 API calls
  egress {
    description = "Allow outbound HTTPS for AWS APIs (ECR, CloudWatch, S3)"
    from_port   = 443
    to_port     = 443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-ecs-tasks-sg-${var.environment}"
  }
}
