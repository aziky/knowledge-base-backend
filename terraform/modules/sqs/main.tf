# Module SQS - Main Resources (simplified for personal project)
resource "aws_sqs_queue" "this" {
  name                       = var.queue_name
  visibility_timeout_seconds = var.visibility_timeout_seconds
  message_retention_seconds  = var.message_retention_seconds

  tags = merge({
    Name        = var.queue_name
    Environment = "Personal"
    Project     = "DemoTerraform"
  }, var.tags)
}

# Dead Letter Queue (simplified)
resource "aws_sqs_queue" "dlq" {
  name = "${var.queue_name}-dlq"

  tags = merge({
    Name        = "${var.queue_name}-dlq"
    Environment = "Personal"
    Project     = "DemoTerraform"
    Type        = "DLQ"
  }, var.tags)
}

# Redrive policy để gửi failed messages đến DLQ
resource "aws_sqs_queue_redrive_policy" "this" {
  queue_url = aws_sqs_queue.this.id
  
  redrive_policy = jsonencode({
    deadLetterTargetArn = aws_sqs_queue.dlq.arn
    maxReceiveCount     = 3
  })
}