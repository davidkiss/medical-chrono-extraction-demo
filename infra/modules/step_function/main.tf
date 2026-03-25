resource "aws_iam_role" "sfn_exec" {
  name = "${var.name}-role"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "states.amazonaws.com"
        }
      }
    ]
  })

  tags = var.tags
}

resource "aws_iam_policy" "sfn_lambda_invoke" {
  name        = "${var.name}-lambda-invoke"
  description = "Allows Step Functions to invoke the chronology Lambdas"

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect   = "Allow"
        Action   = "lambda:InvokeFunction"
        Resource = [
          var.load_pdf_lambda_arn,
          var.extract_chunk_lambda_arn,
          var.group_events_lambda_arn,
          var.dedup_group_lambda_arn,
          var.export_csv_lambda_arn
        ]
      }
    ]
  })
}

resource "aws_iam_role_policy_attachment" "sfn_lambda_invoke" {
  role       = aws_iam_role.sfn_exec.name
  policy_arn = aws_iam_policy.sfn_lambda_invoke.arn
}

resource "aws_sfn_state_machine" "this" {
  name     = var.name
  role_arn = aws_iam_role.sfn_exec.arn

  definition = templatefile("${path.module}/asl.json.tftpl", {
    load_pdf_lambda_arn      = var.load_pdf_lambda_arn
    extract_chunk_lambda_arn  = var.extract_chunk_lambda_arn
    group_events_lambda_arn   = var.group_events_lambda_arn
    dedup_group_lambda_arn    = var.dedup_group_lambda_arn
    export_csv_lambda_arn     = var.export_csv_lambda_arn
  })

  tags = var.tags
}
