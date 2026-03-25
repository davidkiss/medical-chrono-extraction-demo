import io
import os
import boto3
import pandas as pd
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List
from agent.models import MedChronoEvent
from agent.aws.s3_utils import load_json_from_s3, parse_s3_uri

s3_client = boto3.client('s3')

def handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    AWS Lambda handler for exporting final deduplicated results to CSV.
    
    Input event:
    {
        "deduped_uris": ["s3://bucket/path/2024-03-22_deduped.json", ...],
        "pdf_path": "original/pdf/path.pdf",
        "csv_output_uri": "s3://bucket/output/chronology.csv" (optional)
    }
    """
    deduped_uris = event['deduped_uris']
    pdf_path = event['pdf_path']
    pdf_filename = os.path.basename(pdf_path)
    
    # 1. Load all deduped results in parallel
    print(f"Loading {len(deduped_uris)} deduplicated groups...")
    all_events_nested = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        all_events_nested = list(executor.map(load_json_from_s3, deduped_uris))
    
    # 2. Flatten and convert to dictionaries for CSV
    all_event_dicts = []
    for events_list in all_events_nested:
        for event_dict in events_list:
            all_event_dicts.append(event_dict)
            
    print(f"Total deduplicated events: {len(all_event_dicts)}")
    
    # 3. Sort by date, then event_id (matching LangGraph logic)
    all_event_dicts.sort(key=lambda x: (x.get('date', ''), x.get('event_id', '')))
    
    # 4. Generate CSV buffer
    df = pd.DataFrame(all_event_dicts)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding='utf-8')
    
    # 5. Save to S3
    if 'csv_output_uri' in event:
        output_uri = event['csv_output_uri']
    else:
        # Default output location
        bucket_name = parse_s3_uri(deduped_uris[0])[0]
        output_uri = f"s3://{bucket_name}/output/{os.path.splitext(pdf_filename)[0]}_chronology.csv"
        
    out_bucket, out_key = parse_s3_uri(output_uri)
    print(f"Saving final CSV to {output_uri}...")
    
    s3_client.put_object(
        Bucket=out_bucket,
        Key=out_key,
        Body=csv_buffer.getvalue(),
        ContentType='text/csv'
    )
    
    return {
        "success": True,
        "event_count": len(all_event_dicts),
        "csv_output_uri": output_uri
    }
