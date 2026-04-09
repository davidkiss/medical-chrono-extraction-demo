import os
from typing import Any, Dict
from agent.models import ChunkData
from agent.aws.s3_utils import load_json_from_s3, save_json_to_s3, parse_s3_uri
from agent.aws.secrets_utils import get_llm_api_key


def handler(event: Dict[str, Any], context: Any) -> str:
    """
    AWS Lambda handler for extracting events from a single chunk.
    
    Input event:
    {
        "chunk_uri": "s3://bucket/intermediate/chunks/chunk_0.json",
        "pdf_path": "original/pdf/path.pdf",
        "output_bucket": "bucket-name" (optional)
    }
    """
    env_var_name, value = get_llm_api_key()
    os.environ[env_var_name] = value
    from agent.nodes.extract import extract_events

    chunk_uri = event['chunk_uri']
    pdf_path = event['pdf_path']
    bucket, key = parse_s3_uri(chunk_uri)
    output_bucket = event.get('output_bucket', bucket)
    
    # 1. Load chunk data
    print(f"Loading chunk from {chunk_uri}...")
    chunk_dict = load_json_from_s3(chunk_uri)
    chunk = ChunkData(**chunk_dict)
    
    # 2. Extract events
    print(f"Extracting events from chunk {chunk.chunk_id}...")
    events = extract_events(chunk, pdf_path)
    
    # 3. Save extracted events to S3
    # Group results in extraction/[original_pdf_name]/
    pdf_filename = os.path.basename(pdf_path)
    extraction_key = f"intermediate/{pdf_filename}/extractions/chunk_{chunk.chunk_id}_events.json"
    extraction_uri = f"s3://{output_bucket}/{extraction_key}"
    
    print(f"Saving {len(events)} events to {extraction_uri}...")
    # Convert list of Pydantic models to dicts for S3 storage
    save_json_to_s3(extraction_uri, [e.model_dump() for e in events])
    
    return extraction_uri
