import boto3
import json
from typing import Any, Tuple
from urllib.parse import urlparse

s3 = boto3.client('s3')

def parse_s3_uri(uri: str) -> Tuple[str, str]:
    """Parse s3://bucket/key into (bucket, key)."""
    parsed = urlparse(uri)
    if parsed.scheme != 's3':
        raise ValueError(f"Invalid S3 URI: {uri}")
    return parsed.netloc, parsed.path.lstrip('/')

def save_json_to_s3(uri: str, data: Any):
    """Save serializable data to S3 as JSON."""
    bucket, key = parse_s3_uri(uri)
    s3.put_object(
        Bucket=bucket,
        Key=key,
        Body=json.dumps(data, default=str),
        ContentType='application/json'
    )

def load_json_from_s3(uri: str) -> Any:
    """Load JSON data from S3."""
    bucket, key = parse_s3_uri(uri)
    response = s3.get_object(Bucket=bucket, Key=key)
    return json.loads(response['Body'].read().decode('utf-8'))
