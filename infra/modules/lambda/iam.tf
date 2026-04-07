resource "aws_iam_role" "lambda_exec" {
  name = "${var.function_name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_role_policy_attachment" "lambda_logs" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
}

# S3 Permissions
resource "aws_iam_policy" "s3_access" {
  name        = "${var.function_name}-s3-access"
  description = "Allows Lambda to read/write to the medical chronology bucket"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = [
          "s3:GetObject",
          "s3:HeadObject",
          "s3:GetBucketLocation",
          "s3:GetEncryptionConfiguration",
          "s3:PutObject",
          "s3:ListBucket",
          "s3:DeleteObject"
        ]
        Resource = ["*"]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "s3_access" {
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.s3_access.arn
}

# Bedrock Permissions (Optional, for LLM nodes)
resource "aws_iam_policy" "bedrock_access" {
  count       = var.enable_bedrock ? 1 : 0
  name        = "${var.function_name}-bedrock-access"
  description = "Allows Lambda to invoke Bedrock models"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["bedrock:InvokeModel"]
        Resource = ["*"] # Ideally restricted to specific models
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "bedrock_access" {
  count      = var.enable_bedrock ? 1 : 0
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.bedrock_access[0].arn
}

# Secrets Manager Permissions (Optional, for LLM nodes)
resource "aws_iam_policy" "secrets_manager_access" {
  count       = var.enable_secrets_manager ? 1 : 0
  name        = "${var.function_name}-secrets-manager-access"
  description = "Allows Lambda to fetch secrets from AWS Secrets Manager"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = ["secretsmanager:GetSecretValue"]
        Resource = ["*"] # Ideally restricted to specific secrets
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "secrets_manager_access" {
  count      = var.enable_secrets_manager ? 1 : 0
  role       = aws_iam_role.lambda_exec.name
  policy_arn = aws_iam_policy.secrets_manager_access[0].arn
}
