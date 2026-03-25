import asyncio
from datetime import timedelta
from typing import List, TypedDict
from temporalio import workflow
from temporalio.common import RetryPolicy

with workflow.unsafe.imports_passed_through():
    from agent.models import ChunkData, MedChronoEvent
    from agent.nodes.dedup import group_events_by_date
    from agent.temporal.activities import (
        load_and_chunk_pdf_activity,
        extract_chunk_activity,
        dedup_group_activity,
        export_csv_activity,
        ChunkExtractionInput,
        DedupInput,
        ExportInput,
    )


class ExtractionRequest(TypedDict):
    """Input for the Chrono workflow."""
    pdf_path: str
    csv_output_path: str


class ExtractionResult(TypedDict):
    """Output for the Chrono workflow."""
    success: bool
    event_count: int
    csv_output_path: str
    errors: List[str]


@workflow.defn
class MedicalChronoExtractionWorkflow:
    """
    Workflow for medical chronology extraction.
    """

    @workflow.run
    async def run(self, request: ExtractionRequest) -> ExtractionResult:
        errors = []
        
        # Define common retry policy
        retry_policy = RetryPolicy(
            initial_interval=timedelta(seconds=2),
            maximum_attempts=10,
            backoff_coefficient=2.0,
        )

        # 1. Load PDF and chunk
        chunks: List[ChunkData] = await workflow.execute_activity(
            load_and_chunk_pdf_activity,
            request['pdf_path'],
            start_to_close_timeout=timedelta(minutes=5),
            retry_policy=retry_policy,
        )

        # 2. Parallel Extraction Trigger
        extract_tasks = [
            workflow.execute_activity(
                extract_chunk_activity,
                ChunkExtractionInput(chunk=chunk, pdf_path=request['pdf_path']),
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy,
            )
            for chunk in chunks
        ]
        
        extraction_results_nested = await asyncio.gather(*extract_tasks, return_exceptions=True)
        
        all_extracted_events = []
        for i, res in enumerate(extraction_results_nested):
            if isinstance(res, Exception):
                errors.append(f"Chunk {chunks[i].chunk_id} error: {str(res)}")
            else:
                all_extracted_events.extend(res)

        if not all_extracted_events:
            return {
                "success": False,
                "event_count": 0,
                "csv_output_path": "",
                "errors": errors + ["No events extracted from PDF."],
            }

        # 3. Grouping Logic
        events_by_date = group_events_by_date(all_extracted_events)

        # 4. Parallel Deduplication Trigger
        dedup_tasks = [
            workflow.execute_activity(
                dedup_group_activity,
                DedupInput(date=date, events=events),
                start_to_close_timeout=timedelta(minutes=10),
                retry_policy=retry_policy,
            )
            for date, events in events_by_date.items()
        ]

        dedup_results_nested = await asyncio.gather(*dedup_tasks, return_exceptions=True)
        
        final_dedup_results = []
        for i, (date, _) in enumerate(events_by_date.items()):
            res = dedup_results_nested[i]
            if isinstance(res, Exception):
                errors.append(f"Dedup error for date {date}: {str(res)}")
                final_dedup_results.extend(events_by_date[date])
            else:
                final_dedup_results.extend(res)

        # 5. Export to CSV
        await workflow.execute_activity(
            export_csv_activity,
            ExportInput(events=final_dedup_results, csv_output_path=request['csv_output_path']),
            start_to_close_timeout=timedelta(minutes=2),
            retry_policy=retry_policy,
        )

        return {
            "success": True,
            "event_count": len(final_dedup_results),
            "csv_output_path": request['csv_output_path'],
            "errors": errors,
        }
