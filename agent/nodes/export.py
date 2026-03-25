import pandas as pd  # type: ignore
from pathlib import Path
from typing import List

from agent.models import MedChronoEvent

def export_to_csv(events: List[MedChronoEvent], output_path: str) -> None:
    """
    Export events to CSV file.
    
    - One row per event
    - Sorted by date, then event_id
    - UTF-8 encoding with proper escaping
    - Headers match MedChronoEvent fields
    """
    # Convert to dicts
    event_dicts = [event.model_dump() for event in events]
    

    # Sort by date, then event_id
    event_dicts.sort(key=lambda x: (x.get('date') or '', x['event_id']))
    
    # Create DataFrame
    df = pd.DataFrame(event_dicts)
    
    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    
    # Write CSV
    df.to_csv(output_path, index=False, encoding='utf-8')
