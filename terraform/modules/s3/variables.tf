# Module S3 - Variables (simplified for personal project)
variable "bucket_name" {
  description = "Tên của S3 bucket"
  type        = string
}

variable "force_destroy" {
  description = "Có cho phép xóa bucket khi còn object không"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags cho bucket"
  type        = map(string)
  default     = {}
}