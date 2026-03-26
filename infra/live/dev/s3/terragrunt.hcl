# S3 Bucket configuration for dev
include "root" {
  path = find_in_parent_folders()
}

terraform {
  source = "../../../modules/s3"
}

inputs = {
  bucket_name = "medical-chronology-dev-dk-2026"
  environment = "dev"
}
