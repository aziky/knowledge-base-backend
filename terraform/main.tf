terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  required_version = ">= 1.3.0"
}

provider "aws" {
  region = var.aws_region
}

# 🪣 S3 Module
module "s3_bucket" {
  source = "./modules/s3"
  
  bucket_name   = var.s3_bucket_name
  force_destroy = var.s3_force_destroy
  
  tags = var.additional_tags
}

# 📬 SQS Module
module "sqs_queue" {
  source = "./modules/sqs"
  
  queue_name                 = var.sqs_queue_name
  visibility_timeout_seconds = var.sqs_visibility_timeout
  message_retention_seconds  = var.sqs_message_retention
  
  tags = var.additional_tags
}

# � Email Queue Module
module "email_queue" {
  source = "./modules/sqs"
  
  queue_name                 = var.email_queue_name
  visibility_timeout_seconds = var.email_queue_visibility_timeout
  message_retention_seconds  = var.email_queue_message_retention
  
  tags = merge(var.additional_tags, {
    Purpose = "Email Processing"
  })
}

# 🗄️ RDS PostgreSQL Module
module "rds_postgres" {
  source = "./modules/rds"
  
  db_identifier     = var.db_identifier
  db_name          = var.db_name
  db_username      = var.db_username
  db_password      = var.db_password
  db_instance_class = var.db_instance_class
  allocated_storage = var.allocated_storage
  publicly_accessible = var.publicly_accessible
  
  tags = merge(var.additional_tags, {
    Purpose = "Knowledge Base Database"
  })
}

resource "aws_sqs_queue_policy" "s3_to_sqs_policy" {
  queue_url = module.sqs_queue.queue_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid = "AllowS3SendMessage"
        Effect = "Allow"
        Principal = "*"
        Action = "sqs:SendMessage"
        Resource = module.sqs_queue.queue_arn
        Condition = {
          ArnEquals = {
            "aws:SourceArn" = module.s3_bucket.bucket_arn
          }
        }
      }
    ]
  })
}

# 📧 SES Module
module "ses_service" {
  source = "./modules/ses"
  
  name_prefix         = var.ses_name_prefix
  email_addresses     = var.ses_email_addresses
  create_smtp_user    = var.ses_create_smtp_user
  ses_region         = var.aws_region
  
  tags = merge(var.additional_tags, {
    Purpose = "Email Service"
  })
}