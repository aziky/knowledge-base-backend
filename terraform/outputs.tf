# Outputs cho project chính

# S3 Outputs
output "s3_bucket_id" {
  description = "ID của S3 bucket"
  value       = module.s3_bucket.bucket_id
}

output "s3_bucket_arn" {
  description = "ARN của S3 bucket"
  value       = module.s3_bucket.bucket_arn
}

output "s3_bucket_domain_name" {
  description = "Domain name của S3 bucket"
  value       = module.s3_bucket.bucket_domain_name
}

# SQS Outputs
output "sqs_queue_id" {
  description = "ID của SQS queue"
  value       = module.sqs_queue.queue_id
}

output "sqs_queue_arn" {
  description = "ARN của SQS queue"
  value       = module.sqs_queue.queue_arn
}

output "sqs_queue_url" {
  description = "URL của SQS queue"
  value       = module.sqs_queue.queue_url
}

output "sqs_dlq_arn" {
  description = "ARN của Dead Letter Queue"
  value       = module.sqs_queue.dlq_arn
}

output "sqs_dlq_url" {
  description = "URL của Dead Letter Queue"
  value       = module.sqs_queue.dlq_url
}

# Email Queue Outputs
output "email_queue_id" {
  description = "ID của Email SQS queue"
  value       = module.email_queue.queue_id
}

output "email_queue_arn" {
  description = "ARN của Email SQS queue"
  value       = module.email_queue.queue_arn
}

output "email_queue_url" {
  description = "URL của Email SQS queue"
  value       = module.email_queue.queue_url
}

output "email_dlq_arn" {
  description = "ARN của Email Dead Letter Queue"
  value       = module.email_queue.dlq_arn
}

output "email_dlq_url" {
  description = "URL của Email Dead Letter Queue"
  value       = module.email_queue.dlq_url
}

# RDS PostgreSQL Outputs
output "db_endpoint" {
  description = "RDS PostgreSQL endpoint"
  value       = module.rds_postgres.db_instance_endpoint
}

output "db_port" {
  description = "RDS PostgreSQL port"
  value       = module.rds_postgres.db_instance_port
}

output "db_name" {
  description = "Database name"
  value       = module.rds_postgres.db_instance_name
}

output "db_username" {
  description = "Database username"
  value       = module.rds_postgres.db_instance_username
  sensitive   = true
}

output "db_connection_string" {
  description = "PostgreSQL connection string"
  value       = module.rds_postgres.connection_string
  sensitive   = true
}

output "db_security_group_id" {
  description = "Security group ID cho RDS"
  value       = module.rds_postgres.db_security_group_id
}