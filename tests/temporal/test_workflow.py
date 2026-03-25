import asyncio
import pytest
from datetime import timedelta
from temporalio import activity
from temporalio.worker import Worker
from temporalio.testing import WorkflowEnvironment

from agent.temporal.workflow import MedicalChronoExtractionWorkflow, ExtractionRequest
from agent.models import ChunkData, MedChronoEvent
from agent.temporal.activities import ChunkExtractionInput, DedupInput, ExportInput

# Mock Activities
@activity.defn(name="load_and_chunk_pdf_activity")
async def mock_load_pdf(pdf_path: str) -> list[ChunkData]:
    return [ChunkData(chunk_id=0, chunk_text="test", start_page=1, end_page=1, total_pages=1)]

@activity.defn(name="extract_chunk_activity")
async def mock_extract_chunk(input: ChunkExtractionInput) -> list[MedChronoEvent]:
    return [MedChronoEvent(event_id="evt_123", date="2024-01-01", event_type="visit", event_summary="test")]

@activity.defn(name="dedup_group_activity")
async def mock_dedup_group(input: DedupInput) -> list[MedChronoEvent]:
    return input['events']

@activity.defn(name="export_csv_activity")
async def mock_export_csv(input: ExportInput) -> str:
    return input['csv_output_path']

@pytest.mark.asyncio
async def test_workflow_orchestration():
    """Test the full workflow orchestration using Temporal in-memory environment."""
    async with await WorkflowEnvironment.start_time_skipping() as env:
        # Start the worker with mocked activities
        async with Worker(
            env.client,
            task_queue="test-task-queue",
            workflows=[MedicalChronoExtractionWorkflow],
            activities=[mock_load_pdf, mock_extract_chunk, mock_dedup_group, mock_export_csv],
        ):
            # Start workflow
            request: ExtractionRequest = {
                "pdf_path": "fake.pdf",
                "csv_output_path": "fake.csv"
            }
            
            result = await env.client.execute_workflow(
                MedicalChronoExtractionWorkflow.run,
                request,
                id="test-workflow-id",
                task_queue="test-task-queue",
            )
            
            assert result["success"] is True
            assert result["event_count"] == 1
            assert result["csv_output_path"] == "fake.csv"
            assert not result["errors"]
