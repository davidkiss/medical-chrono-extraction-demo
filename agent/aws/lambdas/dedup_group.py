import os
from typing import Any, Dict
from agent.models import MedChronoEvent
from agent.nodes.dedup import deduplicate_single_date_group
from agent.aws.s3_utils import load_json_from_s3, save_json_to_s3, parse_s3_uri

def handler(event: Dict[str, Any], context: Any) -> str:
    """
    AWS Lambda handler for deduplicating events for a single date group.
    
    Input event:
    {
        "date": "2024-03-22",
        "group_uri": "s3://bucket/intermediate/groups/2024-03-22.json",
        "pdf_path": "original/pdf/path.pdf",
        "output_bucket": "bucket-name" (optional)
    }
    """
    date = event['date']
    group_uri = event['group_uri']
    pdf_path = event['pdf_path']
    bucket, key = parse_s3_uri(group_uri)
    output_bucket = event.get('output_bucket', bucket)
    
    # 1. Load date group from S3
    print(f"Loading group for {date} from {group_uri}...")
    events_dict = load_json_from_s3(group_uri)
    events = [MedChronoEvent(**e) for e in events_dict]
    
    # 2. Deduplicate using LLM
    print(f"Deduplicating {len(events)} events for date {date}...")
    deduped_events = deduplicate_single_date_group(date, events)
    
    # 3. Save deduped results back to S3
    pdf_filename = os.path.basename(pdf_path)
    safe_date = date.replace("/", "-").replace(" ", "_")
    deduped_key = f"intermediate/{pdf_filename}/deduped/{safe_date}.json"
    deduped_uri = f"s3://{output_bucket}/{deduped_key}"
    
    print(f"Saving {len(deduped_events)} deduplicated events to {deduped_uri}...")
    save_json_to_s3(deduped_uri, [e.model_dump() for e in deduped_events])
    
    return deduped_uri
