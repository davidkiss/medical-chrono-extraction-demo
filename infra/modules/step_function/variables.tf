variable "name" {
  description = "Name of the Step Function state machine"
  type        = string
}

variable "load_pdf_lambda_arn" {
  description = "ARN of the LoadPdf Lambda function"
  type        = string
}

variable "extract_chunk_lambda_arn" {
  description = "ARN of the ExtractChunk Lambda function"
  type        = string
}

variable "group_events_lambda_arn" {
  description = "ARN of the GroupEvents Lambda function"
  type        = string
}

variable "dedup_group_lambda_arn" {
  description = "ARN of the DedupGroup Lambda function"
  type        = string
}

variable "export_csv_lambda_arn" {
  description = "ARN of the ExportCsv Lambda function"
  type        = string
}

variable "s3_bucket_arn" {
  description = "ARN of the S3 bucket for data storage"
  type        = string
}

variable "tags" {
  description = "A map of tags to add to all resources"
  type        = map(string)
  default     = {}
}
