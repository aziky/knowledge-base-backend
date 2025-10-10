# Module SQS - Variables (simplified for personal project)
variable "queue_name" {
  description = "Tên của SQS queue"
  type        = string
}

variable "visibility_timeout_seconds" {
  description = "Visibility timeout trong giây"
  type        = number
  default     = 30
}

variable "message_retention_seconds" {
  description = "Thời gian giữ message trong giây"
  type        = number
  default     = 86400 # 1 ngày
}

variable "tags" {
  description = "Tags cho queue"
  type        = map(string)
  default     = {}
}