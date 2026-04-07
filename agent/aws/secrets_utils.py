import boto3
import json
import os

def get_secret(secret_id: str) -> str:
    """Fetch secret from AWS Secrets Manager."""
    if not secret_id:
        raise ValueError("Secret ID is required")

    secrets_manager = boto3.client("secretsmanager")
    response = secrets_manager.get_secret_value(SecretId=secret_id)
    secret_string = response.get("SecretString")
    if not secret_string:
        raise ValueError("Secret not found")
    secret_data = json.loads(secret_string)
    return secret_data.get("secret", secret_string)

def get_google_api_key() -> str:
    """Fetch GOOGLE_API_KEY from AWS Secrets Manager."""
    secret_id = os.environ.get("GOOGLE_API_KEY_SECRET_ID")
    return get_secret(secret_id)
