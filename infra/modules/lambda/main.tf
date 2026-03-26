resource "aws_s3_object" "lambda_code" {
  count = var.s3_bucket != "" ? 1 : 0

  bucket = var.s3_bucket
  key    = var.s3_key != "" ? var.s3_key : "lambda/${var.function_name}/lambda_bundle.zip"
  source = var.source_path

  etag = filemd5(var.source_path)
}

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  role          = aws_iam_role.lambda_exec.arn
  handler       = var.handler
  runtime       = var.runtime
  memory_size   = var.memory_size
  timeout       = var.timeout

  s3_bucket = var.s3_bucket != "" ? aws_s3_object.lambda_code[0].bucket : null
  s3_key    = var.s3_bucket != "" ? aws_s3_object.lambda_code[0].key : null
  filename  = var.s3_bucket == "" ? var.source_path : null

  source_code_hash = filebase64sha256(var.source_path)

  layers = var.layers

  environment {
    variables = var.environment_variables
  }

  tags = var.tags
}

resource "aws_cloudwatch_log_group" "this" {
  name              = "/aws/lambda/${var.function_name}"
  retention_in_days = 14
}
