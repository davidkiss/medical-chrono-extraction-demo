"""Deduplication node for removing duplicate medical events by date."""

from collections import defaultdict

from agent.llm.prompts import DEDUP_PROMPT
from agent.llm.provider import get_structured_llm
from agent.models import MedChronoEvent, DedupResult


def group_events_by_date(events: list[MedChronoEvent]) -> dict[str, list[MedChronoEvent]]:
    """Group events by their date field."""
    events_by_date: dict[str, list[MedChronoEvent]] = defaultdict(list)
    for event in events:
        events_by_date[event.date].append(event)
    return events_by_date


def deduplicate_single_date_group(date: str, date_events: list[MedChronoEvent]) -> list[MedChronoEvent]:
    """
    Deduplicate a single group of events for a specific date using LLM.
    
    Args:
        date: The date string for this group
        date_events: List of MedChronoEvent objects for this date
        
    Returns:
        List of deduplicated MedChronoEvent objects
    """
    if len(date_events) <= 1:
        return date_events

    # Build prompt with event details
    events_text = ""
    for evt in date_events:
        events_text += (
            f"- Event {evt.event_id}: facility={evt.facility_name}, "
            f"doctor={evt.doctor_name}, type={evt.event_type}, "
            f"summary={evt.event_summary}, treatment={evt.treatment}\n"
        )

    prompt = DEDUP_PROMPT.format(date=date, events=events_text)

    try:
        llm = get_structured_llm(DedupResult, use_cache=False)
        duplicate_groups: DedupResult = llm.invoke(prompt)
    except Exception as e:
        print(f"Error deduplicating group for date {date}: {e}")
        return date_events

    # Find events to remove
    events_to_remove: set[str] = set()
    for group in duplicate_groups.duplicate_groups:
        if len(group) > 1:
            # Keep first, mark rest for removal
            events_to_remove.update(group[1:])

    # Return non-duplicate events
    return [evt for evt in date_events if evt.event_id not in events_to_remove]


def deduplicate_events_by_date(events: list[MedChronoEvent]) -> list[MedChronoEvent]:
    """
    Deduplicate events by grouping by date and using LLM to identify duplicates.

    For each date:
    1. Send all events to LLM
    2. LLM returns groups of duplicate event IDs
    3. Keep only first event from each group
    4. Remove duplicates

    Runs in parallel per date when called from LangGraph.

    Args:
        events: List of MedChronoEvent objects to deduplicate

    Returns:
        List of deduplicated MedChronoEvent objects
    """
    # Group events by date
    events_by_date = group_events_by_date(events)

    deduped_events: list[MedChronoEvent] = []

    for date, date_events in events_by_date.items():
        deduped_events.extend(deduplicate_single_date_group(date, date_events))

    return deduped_events
