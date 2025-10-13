# Module SES - Outputs

output "domain_identity_arn" {
  description = "ARN of the SES domain identity"
  value       = var.domain_name != "" ? aws_ses_domain_identity.this[0].arn : null
}

output "domain_identity_verification_token" {
  description = "Domain verification token for DNS TXT record"
  value       = var.domain_name != "" ? aws_ses_domain_identity.this[0].verification_token : null
}

output "email_identities" {
  description = "Map of verified email identities"
  value       = { for k, v in aws_ses_email_identity.this : k => v.arn }
}

output "configuration_set_name" {
  description = "Name of the SES configuration set"
  value       = aws_ses_configuration_set.this.name
}

output "configuration_set_arn" {
  description = "ARN of the SES configuration set"
  value       = aws_ses_configuration_set.this.arn
}

output "smtp_username" {
  description = "SMTP username (IAM access key ID)"
  value       = var.create_smtp_user ? aws_iam_access_key.ses_smtp[0].id : null
  sensitive   = true
}

output "smtp_password" {
  description = "SMTP password (IAM secret access key)"
  value       = var.create_smtp_user ? aws_iam_access_key.ses_smtp[0].secret : null
  sensitive   = true
}

output "smtp_server" {
  description = "SES SMTP server endpoint"
  value       = "email-smtp.${var.ses_region}.amazonaws.com"
}

output "smtp_port" {
  description = "SES SMTP port (587 for TLS, 465 for SSL)"
  value       = 587
}

output "domain_dkim_tokens" {
  description = "DKIM tokens for domain verification (if domain is configured)"
  value       = var.domain_name != "" ? aws_ses_domain_identity.this[0].verification_token : null
}

output "ses_region" {
  description = "AWS region where SES resources are created"
  value       = var.ses_region
}

output "verified_email_addresses" {
  description = "List of verified email addresses"
  value       = var.email_addresses
}