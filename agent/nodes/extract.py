"""Extraction node for parallel medical event extraction from PDF chunks."""

from datetime import datetime
import logging
import uuid

from agent.llm.prompts import EXTRACTION_PROMPT
from agent.llm.provider import get_structured_llm
from agent.models import ChunkData, MedChronoEvent, MedChronoEventList

logger = logging.getLogger(__name__)

def extract_events(chunk: ChunkData, source_file: str) -> list[MedChronoEvent]:
    """
    Extract medical events from a PDF chunk using LLM.

    Retries with exponential backoff on API failures.
    Returns list of MedChronoEvent objects with proper metadata.

    Args:
        chunk: ChunkData object containing text and page range
        source_file: Source PDF filename for traceability

    Returns:
        List of MedChronoEvent objects with complete metadata
    """
    prompt = EXTRACTION_PROMPT.format(chunk_text=chunk.chunk_text)
    llm = get_structured_llm(MedChronoEventList)
    event_list = llm.invoke(prompt)

    for event in event_list.events:
        event.event_id = f"evt_{uuid.uuid4().hex[:8]}"
        event.chunk_id = chunk.chunk_id
        event.source_file = source_file
        event.processing_timestamp = datetime.now()

    return event_list.events
