# Configuration cho personal project (simplified)
aws_region = "ap-southeast-1"

# S3 Configuration
s3_bucket_name   = "kb-bucket-personal-2025-10-09"
s3_force_destroy = true
  
# SQS Configuration
sqs_queue_name         = "document-queue"
sqs_visibility_timeout = 30
sqs_message_retention  = 86400

# Email Queue Configuration
email_queue_name                = "email-queue"
email_queue_visibility_timeout  = 60
email_queue_message_retention   = 1209600  # 14 days for email processing

# RDS PostgreSQL Configuration
db_identifier     = "knowledge-base-db"
db_name          = "knowledge_base"
db_username      = "postgres"
db_password      = "mypassword"  # Change this!
db_instance_class = "db.t3.micro"
allocated_storage = 20
publicly_accessible = true

# SES Configuration
ses_name_prefix      = "knowledge-base-ses"
ses_email_addresses  = ["pcm230304@gmail.com"]  # Your email for sending
ses_create_smtp_user = true  # Enable SMTP user creation

# Tags
additional_tags = {
  Owner = "Personal"
  Type  = "Demo"
}