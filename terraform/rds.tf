# ==========================================
# RDS Subnet Group (Multi-AZ)
# ==========================================
resource "aws_db_subnet_group" "main" {
  name        = "${var.project_name}-${var.environment}-db-subnet-group"
  description = "Database subnet group spanning public subnets across availability zones"
  subnet_ids  = aws_subnet.public[*].id

  tags = {
    Name = "${var.project_name}-${var.environment}-db-subnet-group"
  }
}

# ==========================================
# Managed PostgreSQL RDS Instance
# ==========================================
resource "aws_db_instance" "app_db" {
  identifier        = "${var.project_name}-${var.environment}-rds"
  engine            = "postgres"
  engine_version    = "15"
  instance_class    = "db.t3.micro"
  allocated_storage = 20
  storage_type      = "gp2"

  db_name  = var.db_name
  username = var.db_username
  password = var.db_password

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [aws_security_group.db.id]

  # Security & Operational Settings
  publicly_accessible = false
  skip_final_snapshot = true
  deletion_protection = false

  tags = {
    Name = "${var.project_name}-${var.environment}-postgres"
  }
}
