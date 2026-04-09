import boto3
import json
import os

def get_env_var_secret(secret_id: str) -> tuple[str, str]:
    """Fetch secret from AWS Secrets Manager."""
    if not secret_id:
        raise ValueError("Secret ID is required")

    secrets_manager = boto3.client("secretsmanager")
    response = secrets_manager.get_secret_value(SecretId=secret_id)
    secret_string = response.get("SecretString")
    if not secret_string:
        raise ValueError("Secret not found")
    secret_data = json.loads(secret_string)
    return secret_data.get("key"), secret_data.get("value")

def get_llm_api_key() -> tuple[str, str]:
    """Fetch an LLM's API key from AWS Secrets Manager."""
    secret_id = os.environ.get("LLM_API_KEY_SECRET_ID")
    return get_env_var_secret(secret_id)
