# Module SES (Simple Email Service) - Main Resources

# SES Domain Identity
resource "aws_ses_domain_identity" "this" {
  count  = var.domain_name != "" ? 1 : 0
  domain = var.domain_name
}

# SES Domain Identity Verification
resource "aws_ses_domain_identity_verification" "this" {
  count      = var.domain_name != "" && var.verify_domain ? 1 : 0
  domain     = aws_ses_domain_identity.this[0].id
  depends_on = [aws_ses_domain_identity.this]

  timeouts {
    create = "5m"
  }
}

# SES Email Identity (for individual email addresses)
resource "aws_ses_email_identity" "this" {
  for_each = toset(var.email_addresses)
  email    = each.value
}

# SES Configuration Set
resource "aws_ses_configuration_set" "this" {
  name = "${var.name_prefix}-config-set"

  delivery_options {
    tls_policy = "Require"
  }

  reputation_metrics_enabled = true
}

# SES Event Destination for CloudWatch
resource "aws_ses_event_destination" "cloudwatch" {
  name                   = "${var.name_prefix}-cloudwatch"
  configuration_set_name = aws_ses_configuration_set.this.name
  enabled                = true
  matching_types         = ["send", "reject", "bounce", "complaint", "delivery"]

  cloudwatch_destination {
    default_value  = "default"
    dimension_name = "MessageTag"
    value_source   = "messageTag"
  }
}

# SES Identity Policy (allow sending from verified identities)
resource "aws_ses_identity_policy" "sending_policy" {
  count    = var.domain_name != "" ? 1 : 0
  identity = aws_ses_domain_identity.this[0].arn
  name     = "${var.name_prefix}-sending-policy"
  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Principal = {
          AWS = data.aws_caller_identity.current.account_id
        }
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = aws_ses_domain_identity.this[0].arn
      }
    ]
  })
}

# Data source for current AWS account
data "aws_caller_identity" "current" {}

# SES SMTP Credentials (IAM User for SMTP authentication)
resource "aws_iam_user" "ses_smtp" {
  count = var.create_smtp_user ? 1 : 0
  name  = "${var.name_prefix}-ses-smtp-user"
  path  = "/"

  tags = merge({
    Name = "${var.name_prefix}-ses-smtp-user"
  }, var.tags)
}

# IAM Policy for SES sending
resource "aws_iam_user_policy" "ses_smtp" {
  count = var.create_smtp_user ? 1 : 0
  name  = "${var.name_prefix}-ses-smtp-policy"
  user  = aws_iam_user.ses_smtp[0].name

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "ses:SendEmail",
          "ses:SendRawEmail"
        ]
        Resource = "*"
      }
    ]
  })
}

# Access key for SMTP user
resource "aws_iam_access_key" "ses_smtp" {
  count = var.create_smtp_user ? 1 : 0
  user  = aws_iam_user.ses_smtp[0].name
}