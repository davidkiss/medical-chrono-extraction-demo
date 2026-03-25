output "bucket_id" {
  description = "The name of the bucket"
  value       = aws_s3_bucket.this.id
}

output "bucket_arn" {
  description = "The ARN of the bucket"
  value       = aws_s3_bucket.this.arn
}

output "bucket_uri" {
  description = "The S3 URI of the bucket"
  value       = "s3://${aws_s3_bucket.this.id}"
}
