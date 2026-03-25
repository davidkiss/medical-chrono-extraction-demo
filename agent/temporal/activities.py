import os
from typing import List, TypedDict
from temporalio import activity

from agent.models import ChunkData, MedChronoEvent
from agent.utils.pdf_loader import PDFLoader
from agent.nodes.chunking import create_chunks
from agent.nodes.extract import extract_events
from agent.nodes.dedup import deduplicate_single_date_group
from agent.nodes.export import export_to_csv

class ChunkExtractionInput(TypedDict):
    chunk: ChunkData
    pdf_path: str

class DedupInput(TypedDict):
    date: str | None
    events: List[MedChronoEvent]

class ExportInput(TypedDict):
    events: List[MedChronoEvent]
    csv_output_path: str


@activity.defn
async def load_and_chunk_pdf_activity(pdf_path: str) -> List[ChunkData]:
    """Activity to load PDF text and split into chunks."""
    loader = PDFLoader()
    full_text = loader.load(pdf_path)
    total_pages = loader.get_page_count(pdf_path)
    
    chunks = create_chunks(
        full_text,
        total_pages,
        chunk_size=int(os.getenv("CHUNK_SIZE", 50)),
        overlap=int(os.getenv("CHUNK_OVERLAP", 2))
    )
    return chunks


@activity.defn
async def extract_chunk_activity(input: ChunkExtractionInput) -> List[MedChronoEvent]:
    """Activity to extract medical events from a single chunk using LLM."""
    return extract_events(input['chunk'], input['pdf_path'])


@activity.defn
async def dedup_group_activity(input: DedupInput) -> List[MedChronoEvent]:
    """Activity to deduplicate a single date's group of events."""
    return deduplicate_single_date_group(input['date'], input['events'])


@activity.defn
async def export_csv_activity(input: ExportInput) -> str:
    """Activity to export deduplicated events to a CSV file."""
    export_to_csv(input['events'], input['csv_output_path'])
    return input['csv_output_path']
