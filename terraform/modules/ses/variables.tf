# Module SES - Variables

variable "name_prefix" {
  description = "Prefix for SES resource names"
  type        = string
  default     = "ses"
}

variable "domain_name" {
  description = "Domain name for SES domain identity (optional)"
  type        = string
  default     = ""
}

variable "verify_domain" {
  description = "Whether to verify the domain identity"
  type        = bool
  default     = false
}

variable "email_addresses" {
  description = "List of email addresses to verify for SES"
  type        = list(string)
  default     = []
}

variable "create_smtp_user" {
  description = "Whether to create an IAM user for SMTP authentication"
  type        = bool
  default     = false
}

variable "ses_region" {
  description = "AWS region for SES (some features are region-specific)"
  type        = string
  default     = "us-east-1"
}

variable "enable_bounce_complaints" {
  description = "Enable bounce and complaint notifications"
  type        = bool
  default     = true
}

variable "tags" {
  description = "Tags to apply to SES resources"
  type        = map(string)
  default     = {}
}