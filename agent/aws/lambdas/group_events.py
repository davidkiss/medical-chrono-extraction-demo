import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Dict, List
from agent.models import MedChronoEvent
from agent.nodes.dedup import group_events_by_date
from agent.aws.s3_utils import load_json_from_s3, save_json_to_s3, parse_s3_uri

def handler(event: Dict[str, Any], context: Any) -> List[Dict[str, str]]:
    """
    AWS Lambda handler for grouping extracted events by date.
    
    Input event:
    {
        "extraction_uris": ["s3://bucket/path/chunk_0_events.json", ...],
        "pdf_path": "original/pdf/path.pdf",
        "output_bucket": "bucket-name" (optional)
    }
    """
    extraction_uris = event['extraction_uris']
    pdf_path = event['pdf_path']
    output_bucket = event.get('output_bucket', parse_s3_uri(extraction_uris[0])[0])
    
    # 1. Load all extractions in parallel
    print(f"Loading {len(extraction_uris)} extraction results...")
    all_events_nested = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        all_events_nested = list(executor.map(load_json_from_s3, extraction_uris))
    
    # 2. Flatten and convert to MedChronoEvent objects
    all_events = []
    for events_list in all_events_nested:
        for event_dict in events_list:
            all_events.append(MedChronoEvent(**event_dict))
            
    print(f"Total events extracted: {len(all_events)}")
    
    # 3. Group by date
    groups = group_events_by_date(all_events)
    
    # 4. Save groups and return URIs
    pdf_filename = os.path.basename(pdf_path)
    group_info = []
    
    print(f"Saving {len(groups)} date groups to S3...")
    for date, date_events in groups.items():
        # Sanitize date for filename
        safe_date = date.replace("/", "-").replace(" ", "_")
        group_key = f"intermediate/{pdf_filename}/groups/{safe_date}.json"
        group_uri = f"s3://{output_bucket}/{group_key}"
        
        save_json_to_s3(group_uri, [e.model_dump() for e in date_events])
        group_info.append({
            "date": date,
            "group_uri": group_uri,
            "pdf_path": pdf_path
        })
        
    return group_info
