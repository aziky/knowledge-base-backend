# Module RDS PostgreSQL - Variables
variable "db_identifier" {
  description = "Tên identifier cho RDS instance"
  type        = string
}

variable "db_name" {
  description = "Tên database"
  type        = string
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

variable "max_allocated_storage" {
  description = "Dung lượng storage tối đa (GB) cho auto scaling"
  type        = number
  default     = 100
}

variable "backup_retention_period" {
  description = "Số ngày giữ backup"
  type        = number
  default     = 7
}

variable "backup_window" {
  description = "Thời gian backup (UTC)"
  type        = string
  default     = "03:00-04:00"
}

variable "maintenance_window" {
  description = "Thời gian maintenance (UTC)"
  type        = string
  default     = "sun:04:00-sun:05:00"
}

variable "publicly_accessible" {
  description = "Có cho phép truy cập public không"
  type        = bool
  default     = false
}

variable "skip_final_snapshot" {
  description = "Có skip final snapshot khi xóa không"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags cho RDS instance"
  type        = map(string)
  default     = {}
}