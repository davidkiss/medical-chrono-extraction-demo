import io
from typing import List

import pandas as pd  # type: ignore

from agent.models import MedChronoEvent


def events_to_csv_content(events: List[MedChronoEvent]) -> str:
    """
    Convert events to CSV content string.

    - One row per event
    - Sorted by date, then event_id
    - UTF-8 encoding
    - Headers match MedChronoEvent fields

    Returns:
        CSV content as a string
    """
    # Convert to dicts
    event_dicts = [event.model_dump() for event in events]

    # Sort by date, then event_id
    event_dicts.sort(key=lambda x: (x.get("date") or "", x["event_id"]))

    # Create DataFrame and write to buffer
    df = pd.DataFrame(event_dicts)
    csv_buffer = io.StringIO()
    df.to_csv(csv_buffer, index=False, encoding="utf-8")

    return csv_buffer.getvalue()


def export_to_csv(events: List[MedChronoEvent], output_path: str) -> None:
    """
    Export events to CSV file on local filesystem.

    This is a convenience wrapper around events_to_csv_content for file-based output.
    """
    from pathlib import Path

    csv_content = events_to_csv_content(events)

    # Ensure output directory exists
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    # Write CSV
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(csv_content)
