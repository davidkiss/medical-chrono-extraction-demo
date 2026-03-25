# ExportCsv Lambda Configuration
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../../modules/lambda"
}

dependency "s3" {
  config_path = "../../s3"
}

inputs = {
  function_name = "medical-chrono-export-csv-dev"
  handler       = "agent.aws.lambdas.export_csv.handler"
  source_path   = "${get_parent_terragrunt_dir()}/../dist/lambda_bundle.zip"
  s3_bucket_arn = dependency.s3.outputs.bucket_arn
}
