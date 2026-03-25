import os
import operator
from typing import TypedDict, List, Annotated
from langgraph.graph import StateGraph, START, END
from langgraph.graph.state import CompiledStateGraph
from langgraph.types import Send
from dotenv import load_dotenv

from agent.models import ChunkData, MedChronoEvent
from agent.utils.pdf_loader import PDFLoader
from agent.nodes.chunking import create_chunks
from agent.nodes.extract import extract_events
from agent.nodes.dedup import group_events_by_date, deduplicate_single_date_group
from agent.nodes.export import export_to_csv

load_dotenv()



class ChunkProcessingState(TypedDict):
    """Internal state for parallel extraction of a single chunk."""
    chunk: ChunkData
    pdf_path: str

class DedupGroupState(TypedDict):
    """Internal state for parallel deduplication of a single date group."""
    date: str
    events: List[MedChronoEvent]

class ExtractionState(TypedDict):
    """State for medical chronology extraction graph."""
    pdf_path: str
    chunks: List[ChunkData]
    # Results from parallel extraction
    extraction_results: Annotated[List[MedChronoEvent], operator.add]
    # Results from parallel deduplication
    dedup_results: Annotated[List[MedChronoEvent], operator.add]
    errors: Annotated[List[str], operator.add]
    csv_output_path: str

def create_extraction_graph() -> CompiledStateGraph:
    """
    Create LangGraph state graph with parallel processing for both extraction and deduplication.
    
    Processing Flow:
    1. load_pdf: Splits PDF into manageable chunks
    2. Parallel extract: One 'extract_chunk' node per chunk
    3. split_by_date: Groups events by date and triggers parallel dedup
    4. Parallel dedup_group: One node per unique date for LLM-based deduping
    5. export: Saves the medical chronology to a CSV file
    """
    workflow = StateGraph(ExtractionState)

    # 1. Load PDF and chunk
    def load_pdf_node(state: ExtractionState) -> dict:
        loader = PDFLoader()
        full_text = loader.load(state['pdf_path'])
        total_pages = loader.get_page_count(state['pdf_path'])
        chunks = create_chunks(
            full_text, total_pages, 
            chunk_size=int(os.getenv("CHUNK_SIZE", 50)), 
            overlap=int(os.getenv("CHUNK_OVERLAP", 2))
        )
        return {'chunks': chunks}

    # 2. Parallel Extraction Trigger
    def start_extraction_node(state: ExtractionState):
        """Node that returns Sends for parallel extraction of each chunk."""
        return [
            Send("extract_chunk", {"chunk": chunk, "pdf_path": state['pdf_path']})
            for chunk in state['chunks']
        ]

    # 3. Extract events from a single chunk (runs in parallel)
    def extract_chunk_node(state: ChunkProcessingState):
        try:
            events = extract_events(state['chunk'], state['pdf_path'])
            return {'extraction_results': events}
        except Exception as e:
            return {'errors': [f"Chunk {state['chunk'].chunk_id} error: {str(e)}"]}

    # 4. Junction node: waits for ALL extractions to finish
    def prepare_dedup_node(state: ExtractionState) -> dict:
        """Junction point after extraction, before deduplication fan-out."""
        return {}

    # 5. Routing logic for parallel dedup
    def router_to_dedup(state: ExtractionState):
        """Router that returns Sends for parallel dedup of each date group."""
        events_by_date = group_events_by_date(state['extraction_results'])
        
        # Parallelize: send each date group to the 'dedup_group' node
        return [
            Send("dedup_group", {"date": date, "events": events})
            for date, events in events_by_date.items()
        ]

    # 6. Deduplicate a single date group (runs in parallel)
    def dedup_group_node(state: DedupGroupState):
        """Deduplicates a single date's events."""
        try:
            deduped = deduplicate_single_date_group(state['date'], state['events'])
            return {'dedup_results': deduped}
        except Exception as e:
            return {'errors': [f"Dedup error for date {state['date']}: {str(e)}"]}

    # 7. Export to CSV
    def export_node(state: ExtractionState) -> dict:
        export_to_csv(state['dedup_results'], state['csv_output_path'])
        return {}

    # Build the graph
    workflow.add_node("load_pdf", load_pdf_node)
    workflow.add_node("extract_chunk", extract_chunk_node)
    workflow.add_node("prepare_dedup", prepare_dedup_node)
    workflow.add_node("dedup_group", dedup_group_node)
    workflow.add_node("export", export_node)

    workflow.add_edge(START, "load_pdf")
    
    # load_pdf triggers extract_chunk parallel branches via conditional edge
    workflow.add_conditional_edges(
        "load_pdf", 
        start_extraction_node, 
        ["extract_chunk"]
    )
    
    # After ALL extract_chunk nodes finish, merge into prepare_dedup
    workflow.add_edge("extract_chunk", "prepare_dedup")
    
    # prepare_dedup triggers dedup_group parallel branches via conditional edge
    workflow.add_conditional_edges(
        "prepare_dedup",
        router_to_dedup,
        ["dedup_group"]
    )
    
    # After ALL dedup_group nodes finish, finalize with export
    workflow.add_edge("dedup_group", "export")
    workflow.add_edge("export", END)

    return workflow.compile()
