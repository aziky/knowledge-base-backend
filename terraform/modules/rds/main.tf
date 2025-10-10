# Module RDS PostgreSQL - Main Resources
resource "aws_db_instance" "this" {
  identifier = var.db_identifier
  
  # Engine configuration
  engine         = "postgres"
  engine_version = "15.7"
  instance_class = var.db_instance_class
  
  # Database configuration
  db_name  = var.db_name
  username = var.db_username
  password = var.db_password
  
  # Storage configuration
  allocated_storage     = var.allocated_storage
  max_allocated_storage = var.max_allocated_storage
  storage_type          = "gp2"
  storage_encrypted     = true
  
  # Backup configuration
  backup_retention_period = var.backup_retention_period
  backup_window          = var.backup_window
  maintenance_window     = var.maintenance_window
  
  # Network & Security
  publicly_accessible    = var.publicly_accessible
  db_subnet_group_name   = aws_db_subnet_group.this.name
  vpc_security_group_ids = [aws_security_group.rds.id]
  
  # Deletion protection
  deletion_protection   = false
  skip_final_snapshot  = var.skip_final_snapshot
  final_snapshot_identifier = var.skip_final_snapshot ? null : "${var.db_identifier}-final-snapshot"
  
  # Performance Insights
  performance_insights_enabled = true
  performance_insights_retention_period = 7
  
  # Monitoring
  monitoring_interval = 0
  enabled_cloudwatch_logs_exports = ["postgresql"]
  
  tags = merge({
    Name        = var.db_identifier
    Engine      = "PostgreSQL"
    Environment = "Personal"
    Project     = "DemoTerraform"
  }, var.tags)
}

# DB Subnet Group (sẽ dùng default VPC)
resource "aws_db_subnet_group" "this" {
  name       = "${var.db_identifier}-subnet-group"
  subnet_ids = data.aws_subnets.default.ids
  
  tags = merge({
    Name = "${var.db_identifier}-subnet-group"
  }, var.tags)
}

# Data source để lấy default VPC
data "aws_vpc" "default" {
  default = true
}

# Data source để lấy subnets của default VPC
data "aws_subnets" "default" {
  filter {
    name   = "vpc-id"
    values = [data.aws_vpc.default.id]
  }
}

# Security Group cho RDS
resource "aws_security_group" "rds" {
  name        = "${var.db_identifier}-rds-sg"
  description = "Security group for RDS PostgreSQL instance"
  vpc_id      = data.aws_vpc.default.id

  # Cho phép PostgreSQL traffic từ your specific IPs
  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["103.199.68.69/32", "103.199.55.71/32"]
    description = "PostgreSQL access from your IPs only"
  }

  # Cho phép tất cả outbound traffic
  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
    description = "All outbound traffic"
  }

  tags = merge({
    Name = "${var.db_identifier}-rds-sg"
  }, var.tags)
}