# Module SQS - Outputs
output "queue_id" {
  description = "ID của SQS queue"
  value       = aws_sqs_queue.this.id
}

output "queue_arn" {
  description = "ARN của SQS queue"
  value       = aws_sqs_queue.this.arn
}

output "queue_url" {
  description = "URL của SQS queue"
  value       = aws_sqs_queue.this.url
}

output "queue_name" {
  description = "Tên của SQS queue"
  value       = aws_sqs_queue.this.name
}

output "dlq_id" {
  description = "ID của Dead Letter Queue"
  value       = aws_sqs_queue.dlq.id
}

output "dlq_arn" {
  description = "ARN của Dead Letter Queue"
  value       = aws_sqs_queue.dlq.arn
}

output "dlq_url" {
  description = "URL của Dead Letter Queue"
  value       = aws_sqs_queue.dlq.url
}