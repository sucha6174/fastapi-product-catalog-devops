# ==========================================
# API Security Group (Compute Layer)
# ==========================================
resource "aws_security_group" "api" {
  name        = "${var.project_name}-${var.environment}-api-sg"
  description = "Controls inbound traffic to FastAPI application and outbound internet access"
  vpc_id      = aws_vpc.main.id

  # Inbound HTTP traffic on container port
  ingress {
    description = "Allow inbound application traffic"
    from_port   = var.container_port
    to_port     = var.container_port
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Inbound HTTP traffic on standard port 80
  ingress {
    description = "Allow inbound HTTP standard port"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  # Outbound internet traffic (ECR image pulls, CloudWatch logs, OS updates)
  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-api-sg"
  }
}

# ==========================================
# Database Security Group (Least Privilege)
# ==========================================
resource "aws_security_group" "db" {
  name        = "${var.project_name}-${var.environment}-db-sg"
  description = "Restricts PostgreSQL access strictly to the API compute instances"
  vpc_id      = aws_vpc.main.id

  # Inbound PostgreSQL traffic restricted ONLY to the API security group
  ingress {
    description     = "Allow PostgreSQL access strictly from API Security Group"
    from_port       = 5432
    to_port         = 5432
    protocol        = "tcp"
    security_groups = [aws_security_group.api.id]
  }

  # Outbound traffic (none required, but permit egress within VPC)
  egress {
    description = "Allow outbound responses"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = "${var.project_name}-${var.environment}-db-sg"
  }
}
