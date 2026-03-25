import os
import boto3
from typing import Any, Dict, List
from agent.utils.pdf_loader import PDFLoader
from agent.nodes.chunking import create_chunks
from agent.aws.s3_utils import parse_s3_uri, save_json_to_s3

s3_client = boto3.client('s3')

def handler(event: Dict[str, Any], context: Any) -> List[str]:
    """
    AWS Lambda handler for PDF loading and chunking.
    
    Input event:
    {
        "pdf_uri": "s3://bucket/path/to/file.pdf",
        "output_bucket": "bucket-name" (optional, defaults to input bucket)
    }
    """
    pdf_uri = event['pdf_uri']
    bucket, key = parse_s3_uri(pdf_uri)
    output_bucket = event.get('output_bucket', bucket)
    
    local_path = f"/tmp/{os.path.basename(key)}"
    
    # 1. Download PDF
    print(f"Downloading {pdf_uri} to {local_path}...")
    s3_client.download_file(bucket, key, local_path)
    
    # 2. Load and Chunk
    print("Loading and chunking PDF...")
    loader = PDFLoader()
    full_text = loader.load(local_path)
    total_pages = loader.get_page_count(local_path)
    
    chunks = create_chunks(
        full_text, 
        total_pages,
        chunk_size=int(os.getenv("CHUNK_SIZE", 20)),
        overlap=int(os.getenv("CHUNK_OVERLAP", 2))
    )
    
    # 3. Save chunks to S3 and collect URIs
    chunk_uris = []
    base_prefix = f"intermediate/{os.path.splitext(key)[0]}/chunks"
    
    print(f"Saving {len(chunks)} chunks to s3://{output_bucket}/{base_prefix}...")
    for chunk in chunks:
        chunk_key = f"{base_prefix}/chunk_{chunk.chunk_id}.json"
        chunk_uri = f"s3://{output_bucket}/{chunk_key}"
        save_json_to_s3(chunk_uri, chunk.model_dump())
        chunk_uris.append(chunk_uri)
        
    return chunk_uris
