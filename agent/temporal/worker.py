import asyncio
import logging
import os
from dotenv import load_dotenv
from temporalio.client import Client
from temporalio.worker import Worker
from agent.temporal.activities import (
    load_and_chunk_pdf_activity,
    extract_chunk_activity,
    dedup_group_activity,
    export_csv_activity,
)
from agent.temporal.workflow import MedicalChronoExtractionWorkflow

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    # Connect to Temporal server (defaults to localhost:7233)
    client = await Client.connect(os.getenv("TEMPORAL_HOST", "localhost:7233"))
    
    # Run the worker
    worker = Worker(
        client,
        task_queue="medical-chrono-task-queue",
        workflows=[MedicalChronoExtractionWorkflow],
        activities=[
            load_and_chunk_pdf_activity,
            extract_chunk_activity,
            dedup_group_activity,
            export_csv_activity,
        ],
    )
    
    logger.info("Temporal Worker starting for 'medical-chrono-task-queue'...")
    await worker.run()


if __name__ == "__main__":
    asyncio.run(main())
