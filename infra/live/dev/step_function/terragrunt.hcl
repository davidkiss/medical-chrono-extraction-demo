# Step Function configuration for dev
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../modules/step_function"
}

dependency "s3" {
  config_path = "../s3"
}

dependency "load_pdf" {
  config_path = "../lambdas/load_pdf"
}

dependency "extract_chunk" {
  config_path = "../lambdas/extract_chunk"
}

dependency "group_events" {
  config_path = "../lambdas/group_events"
}

dependency "dedup_group" {
  config_path = "../lambdas/dedup_group"
}

dependency "export_csv" {
  config_path = "../lambdas/export_csv"
}

inputs = {
  name                     = "medical-chronology-workflow-dev"
  s3_bucket_arn            = dependency.s3.outputs.bucket_arn
  load_pdf_lambda_arn      = dependency.load_pdf.outputs.function_arn
  extract_chunk_lambda_arn  = dependency.extract_chunk.outputs.function_arn
  group_events_lambda_arn   = dependency.group_events.outputs.function_arn
  dedup_group_lambda_arn    = dependency.dedup_group.outputs.function_arn
  export_csv_lambda_arn     = dependency.export_csv.outputs.function_arn
}
