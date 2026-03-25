"""LLM prompts for medical chronology event extraction."""

EVENT_TYPE_DEFINITIONS = """
- procedure: Surgical or interventional medical procedures, operations, treatments administered
- testing: Diagnostic tests, lab work, imaging, screenings
- consultation: Doctor visits, specialist appointments, evaluations, second opinions
"""

EXTRACTION_PROMPT = """
You are a medical records specialist extracting chronology events from a medical record.

Extract ALL medical events with an event_summary from the following medical record text. For each event, identify:
- date: The date of the event in yyyy-mm-dd format,  
- facility_name: Hospital, clinic, or medical facility name, if available
- doctor_name: Physician or provider name, if available
- event_type: Classify as ONE of:
  - procedure: Surgical or interventional medical procedures, operations, treatments administered
  - testing: Diagnostic tests, lab work, imaging, screenings
  - visit (default): Doctor consultation, specialist appointments, evaluations, second opinions,
- event_summary: Brief description of what occurred,
- treatment: Any treatment or procedure performed, if available
- page: int page number where event appears,
- citation_quote: Exact quote from text with page number (e.g., "Patient underwent MRI [p.15]"),
- confidence_score: Your confidence in this extraction (0.0-1.0),

If a value is not available and cannot be determined for a field, set it to None.

## Medical Record text
{chunk_text}
"""

DEDUP_PROMPT = """
Review these medical events from {date}. Identify which events describe the SAME medical encounter.

Events:
{events}

Return JSON array of duplicate groups of events: [["evt_1", "evt_2"], ["evt_3", "evt_4"]] and their reasoning.
Only group events that are clearly the same encounter described differently.
"""
