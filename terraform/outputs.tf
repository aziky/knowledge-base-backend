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

# Document queue DLQ outputs đã xóa

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

# Email queue DLQ outputs đã xóa

# Video Queue Outputs
output "video_queue_id" {
  description = "ID của Video SQS queue"
  value       = module.video_queue.queue_id
}

output "video_queue_arn" {
  description = "ARN của Video SQS queue"
  value       = module.video_queue.queue_arn
}

output "video_queue_url" {
  description = "URL của Video SQS queue"
  value       = module.video_queue.queue_url
}

# Video queue DLQ outputs đã xóa

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

# SES Outputs
output "ses_email_identities" {
  description = "Map of verified email identities"
  value       = module.ses_service.email_identities
}

output "ses_configuration_set_name" {
  description = "Name of the SES configuration set"
  value       = module.ses_service.configuration_set_name
}

output "ses_smtp_server" {
  description = "SES SMTP server endpoint"
  value       = module.ses_service.smtp_server
}

output "ses_smtp_port" {
  description = "SES SMTP port"
  value       = module.ses_service.smtp_port
}

output "ses_smtp_username" {
  description = "SMTP username (IAM access key ID)"
  value       = module.ses_service.smtp_username
  sensitive   = true
}

output "ses_smtp_password" {
  description = "SMTP password (IAM secret access key)"
  value       = module.ses_service.smtp_password
  sensitive   = true
}