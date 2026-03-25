import asyncio
import argparse
import sys
from datetime import timedelta
from temporalio.client import Client

from agent.temporal.workflow import MedicalChronoExtractionWorkflow


async def run_workflow(pdf_path: str, output_path: str):
    """Start the Medical Chronology Extraction Workflow."""
    # Connect to local Temporal server
    try:
        client = await Client.connect("localhost:7233")
    except Exception as e:
        print(f"Error: Could not connect to Temporal server: {e}")
        print("Make sure you've started the server with 'docker-compose up -d'.")
        sys.exit(1)

    # Generate a unique workflow ID based on the PDF filename
    workflow_id = f"medical-chrono-extraction-{pdf_path.split('/')[-1]}"

    print(f"Starting workflow {workflow_id} for {pdf_path}...")
    
    # Start the workflow and wait for the result
    result = await client.execute_workflow(
        MedicalChronoExtractionWorkflow.run,
        {"pdf_path": pdf_path, "csv_output_path": output_path},
        id=workflow_id,
        task_queue="medical-chrono-task-queue",
        # Set a total workflow runtime timeout (e.g., 30 minutes)
        execution_timeout=timedelta(minutes=30),
    )

    # Print results
    print("\nWorkflow Execution Complete:")
    print(f"Success: {result['success']}")
    print(f"Deduplicated Event Count: {result['event_count']}")
    print(f"Output CSV: {result['csv_output_path']}")
    
    if result['errors']:
        print("\nErrors encountered:")
        for err in result['errors']:
            print(f" - {err}")


def main():
    parser = argparse.ArgumentParser(description="Run the Temporal Medical Chronology Workflow.")
    parser.add_argument("--pdf", required=True, help="Path to the source PDF file")
    parser.add_argument("--output", default="output/temporal_medical_chronology.csv", help="Path for the output CSV file")
    
    args = parser.parse_args()
    
    asyncio.run(run_workflow(args.pdf, args.output))


if __name__ == "__main__":
    main()
