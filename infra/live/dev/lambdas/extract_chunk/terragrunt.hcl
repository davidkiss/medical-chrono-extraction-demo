# ExtractChunk Lambda Configuration
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
  function_name = "medical-chrono-extract-chunk-dev"
  handler       = "agent.aws.lambdas.extract_chunk.handler"
  source_path   = "${get_parent_terragrunt_dir()}/../dist/lambda_bundle.zip"
  s3_bucket_arn = dependency.s3.outputs.bucket_arn
  enable_bedrock = true
  
  environment_variables = {
    LLM_MODEL = "anthropic.claude-3-5-sonnet-20240620-v1:0"
    LLM_TEMPERATURE = "0.0"
    MAX_RETRIES = "3"
  }
}
