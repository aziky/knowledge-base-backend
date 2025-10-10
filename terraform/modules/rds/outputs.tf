# Module RDS PostgreSQL - Outputs
output "db_instance_endpoint" {
  description = "RDS instance endpoint"
  value       = aws_db_instance.this.endpoint
}

output "db_instance_hosted_zone_id" {
  description = "RDS instance hosted zone ID"
  value       = aws_db_instance.this.hosted_zone_id
}

output "db_instance_id" {
  description = "RDS instance ID"
  value       = aws_db_instance.this.id
}

output "db_instance_resource_id" {
  description = "RDS instance resource ID"
  value       = aws_db_instance.this.resource_id
}

output "db_instance_status" {
  description = "RDS instance status"
  value       = aws_db_instance.this.status
}

output "db_instance_name" {
  description = "Database name"
  value       = aws_db_instance.this.db_name
}

output "db_instance_username" {
  description = "Database username"
  value       = aws_db_instance.this.username
  sensitive   = true
}

output "db_instance_port" {
  description = "Database port"
  value       = aws_db_instance.this.port
}

output "db_instance_arn" {
  description = "RDS instance ARN"
  value       = aws_db_instance.this.arn
}

output "db_security_group_id" {
  description = "Security group ID cho RDS"
  value       = aws_security_group.rds.id
}

output "db_subnet_group_name" {
  description = "DB subnet group name"
  value       = aws_db_subnet_group.this.name
}

output "connection_string" {
  description = "PostgreSQL connection string"
  value       = "postgresql://${aws_db_instance.this.username}:[PASSWORD]@${aws_db_instance.this.endpoint}/${aws_db_instance.this.db_name}"
  sensitive   = true
}