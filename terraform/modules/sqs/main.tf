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

# Không sử dụng Dead Letter Queue
# Messages thất bại sẽ vẫn ở trong queue chính để retry liên tục