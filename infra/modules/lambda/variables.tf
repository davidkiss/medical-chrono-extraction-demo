variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "handler" {
  description = "The function entrypoint in your code"
  type        = string
  default     = "handler.handler"
}

variable "runtime" {
  description = "The identifier of the function's runtime"
  type        = string
  default     = "python3.12"
}

variable "memory_size" {
  description = "Amount of memory in MB your Lambda Function can use at runtime"
  type        = number
  default     = 1024
}

variable "timeout" {
  description = "Amount of time your Lambda Function has to run in seconds"
  type        = number
  default     = 300
}

variable "environment_variables" {
  description = "A map that defines environment variables for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "layers" {
  description = "List of Lambda Layer ARNs to attach to the function"
  type        = list(string)
  default     = []
}

variable "source_path" {
  description = "Path to the Lambda function source code (e.g. ZIP file)"
  type        = string
}

variable "s3_bucket" {
  description = "S3 bucket name for Lambda code storage"
  type        = string
  default     = ""
}

variable "s3_key" {
  description = "S3 key for Lambda code storage"
  type        = string
  default     = ""
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket the Lambda needs access to"
  type        = string
}

variable "enable_bedrock" {
  description = "Whether to grant Bedrock invocation permissions to this Lambda"
  type        = bool
  default     = false
}

variable "enable_secrets_manager" {
  description = "Whether to grant Secrets Manager access to this Lambda"
  type        = bool
  default     = false
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
