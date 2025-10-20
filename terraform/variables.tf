# Variables cho personal project (simplified)
variable "aws_region" {
  description = "AWS region để deploy resources"
  type        = string
  default     = "ap-southeast-1" # Singapore
}

# S3 Variables
variable "s3_bucket_name" {
  description = "Tên của S3 bucket"
  type        = string
  default     = "kb-bucket"
}

variable "s3_force_destroy" {
  description = "Có cho phép xóa bucket khi còn object không"
  type        = bool
  default     = true
}

# SQS Variables
variable "sqs_queue_name" {
  description = "Tên của SQS queue"
  type        = string
  default     = "document-queue"
}

variable "sqs_visibility_timeout" {
  description = "Visibility timeout cho SQS queue (giây)"
  type        = number
  default     = 30
}

variable "sqs_message_retention" {
  description = "Thời gian giữ message trong SQS (giây)"
  type        = number
  default     = 86400 # 1 ngày
}

# Email Queue Variables
variable "email_queue_name" {
  description = "Tên của Email SQS queue"
  type        = string
  default     = "email-queue"
}

variable "email_queue_visibility_timeout" {
  description = "Visibility timeout cho Email SQS queue (giây)"
  type        = number
  default     = 30
}

variable "email_queue_message_retention" {
  description = "Thời gian giữ message trong Email SQS (giây)"
  type        = number
  default     = 86400 # 1 ngày
}

# Video Queue Variables
variable "video_queue_name" {
  description = "Tên của Video SQS queue"
  type        = string
  default     = "video-queue"
}

variable "video_queue_visibility_timeout" {
  description = "Visibility timeout cho Video SQS queue (giây)"
  type        = number
  default     = 30
}

variable "video_queue_message_retention" {
  description = "Thời gian giữ message trong Video SQS (giây)"
  type        = number
  default     = 86400 # 1 ngày
}

# RDS PostgreSQL Variables
variable "db_identifier" {
  description = "Tên identifier cho RDS instance"
  type        = string
  default     = "knowledge-base-db"
}

variable "db_name" {
  description = "Tên database"
  type        = string
  default     = "knowledge_base"
}

variable "db_username" {
  description = "Username cho database"
  type        = string
  default     = "postgres"
}

variable "db_password" {
  description = "Password cho database"
  type        = string
  sensitive   = true
}

variable "db_instance_class" {
  description = "Instance class cho RDS"
  type        = string
  default     = "db.t3.micro"
}

variable "allocated_storage" {
  description = "Dung lượng storage (GB)"
  type        = number
  default     = 20
}

variable "publicly_accessible" {
  description = "Có cho phép truy cập public không"
  type        = bool
  default     = false
}

# SES Variables
variable "ses_name_prefix" {
  description = "Prefix for SES resource names"
  type        = string
  default     = "knowledge-base-ses"
}

variable "ses_email_addresses" {
  description = "List of email addresses to verify for SES"
  type        = list(string)
  default     = []
}

variable "ses_create_smtp_user" {
  description = "Whether to create an IAM user for SMTP authentication"
  type        = bool
  default     = false
}

# Common Tags
variable "additional_tags" {
  description = "Tags bổ sung cho resources"
  type        = map(string)
  default     = {}
}