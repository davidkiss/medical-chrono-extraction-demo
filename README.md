# Medical Chronology Extraction AI Workflow

AI workflow for extracting structured medical events from complex legal and medical PDF documents implemented with [LangGraph](https://langchain.com/langgraph), [Temporal.io](https://temporal.io) and [AWS Step Functions](https://aws.amazon.com/step-functions/).

## 🚀 Three Workflow Engines

This project provides three ways to run the medical chronology extraction:

1.  **LangGraph**: Best for low-latency, stateless local runs and interactive development.
2.  **Temporal**: Best for large PDF files, long-running extractions, and production environments where fault tolerance and observability are critical.
3.  **AWS Step Functions**: Best for high-scale, serverless extractions using Amazon Bedrock without managing any infrastructure or API keys.

---

## 🛠 Setup & Installation

### 1. Requirements
- Python 3.11+
- [uv](https://github.com/astral-sh/uv) (Recommended package manager)
- [Temporal CLI](https://docs.temporal.io/cli) (For Temporal engine only)
- [Terraform](https://www.terraform.io/) & [Terragrunt](https://terragrunt.gruntwork.io/) (For AWS Step Functions engine only)
- [AWS CLI](https://aws.amazon.com/cli/) (For AWS Step Functions engine only)

### 2. Install Dependencies
```bash
uv sync --extra dev
```

### 3. Configure Environment
```bash
cp .env.example .env
# Edit .env with your LLM provider and API keys
```

---

## 📉 Workflow 1: LangGraph (Stateless)

The LangGraph engine uses a directed acyclic graph (DAG) with parallel branches for extraction and deduplication.

### Running with LangGraph CLI
The easiest way to explore the LangGraph workflow is via the LangGraph Dev server:
```bash
uv run langgraph dev
```
Then visit the local studio UI to trigger extractions visually.

### Running via Python
```python
from agent.graph import create_extraction_graph

# Initialize
graph = create_extraction_graph()
state = {
    'pdf_path': 'samples/medical-record.pdf',
    'csv_output_path': 'output/chronology_langgraph.csv',
    'extraction_results': [],
    'dedup_results': [],
    'errors': []
}

# Execute
result = graph.invoke(state)
```

---

## 🕰 Workflow 2: Temporal (Fault-Tolerant)

The Temporal engine wraps the same AI logic into durable "Activities" and a "Workflow". If an LLM call fails or your machine crashes mid-extraction, Temporal will resume exactly where it left off.

### 1. Start a Local Temporal Infrastructure

```bash
temporal server start-dev
```

This will start local Temporal server, UI and database.
Visit the Temporal UI at [http://localhost:8233](http://localhost:8233).

### 2. Start the Temporal Worker
The worker listens for extraction tasks:
```bash
uv run python agent/temporal/worker.py
```

### 3. Trigger an Extraction
Use the runner script to send a PDF to the Temporal cluster:
```bash
uv run python agent/temporal/run_workflow.py --pdf samples/sample-medical-chronology.pdf --output output/chronology_temporal.csv
```

---

## ☁️ Workflow 3: AWS Step Functions (Serverless)

The AWS engine uses **Amazon Step Functions** to orchestrate modular **AWS Lambda** functions. It leverages **Amazon Bedrock** (Anthropic Claude/Google Gemini models) for AI processing, eliminating the need for external API keys and managing server infrastructure.

### 1. Build Lambda Packages
Use the build script to bundle the Python code and its dependencies into ZIP files (one for code, one for the Lambda Layer):
```bash
chmod +x scripts/build_lambda.sh
./scripts/build_lambda.sh
```

### 2. Deploy Infrastructure
Deploy the S3 buckets, Lambdas, IAM roles, and the Step Function using Terragrunt:
```bash
cd infra/live/dev
terragrunt apply
```

### 3. Trigger an Extraction
You can trigger the workflow via the AWS Console or using the AWS CLI:
```bash
aws stepfunctions start-execution \
  --state-machine-arn <STEP_FUNCTION_ARN> \
  --input '{
    "pdf_uri": "s3://your-input-bucket/sample.pdf",
    "output_bucket": "your-output-bucket",
    "csv_output_uri": "s3://your-output-bucket/chronology_aws.csv"
  }'
```
*Note: You can find the `<STEP_FUNCTION_ARN>` in the Terragrunt output or AWS Console.*

---

## 📁 Project Structure

```text
├── agent/
│   ├── graph.py           # LangGraph state machine definition
│   ├── temporal/          # Temporal-specific orchestration
│   ├── aws/               # AWS Step Functions & Lambda handlers
│   │   ├── lambdas/       # Individual Lambda function entrypoints
│   │   └── s3_utils.py    # AWS S3 helper functions
│   ├── nodes/             # Core AI logic (shared by all engines)
│   ├── llm/               # Provider abstraction & prompts
│   ├── models.py          # Structured Pydantic data models
│   └── utils/             # PDF loading helpers
├── infra/                 # IaC for AWS Step Functions
│   ├── live/              # Terragrunt environment configurations
│   └── modules/           # Reusable Terraform modules (Lambdas, S3, Step Functions)
├── tests/                 # Comprehensive test suite
├── scripts/               # Build and deployment utilities
└── docker-compose.yml     # Infrastructure for Temporal
```

## 🧪 Running Tests
```bash
# Run all tests (including new Temporal tests)
uv run pytest
```

## 🗝 Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `LLM_MODEL` | Model name (e.g., `openai:gpt-4o`, `anthropic:claude-3-5-sonnet`) | `google_genai:gemini-3-flash-preview` |
| `LLM_TEMPERATURE` | Temperature for LLM | `0.0` |
| `MAX_TOKENS` | Max tokens for LLM | `20000` |
| `MAX_RETRIES` | Max retries for LLM | `3` |
| `CHUNK_SIZE` | Pages per extraction chunk | `20` |
| `CHUNK_OVERLAP`| Overlap pages for context | `2` |
| `REQUEST_TIMEOUT`| API timeout (seconds) | `300` |
| `OPENAI_API_KEY` | Your OpenAI API key (if using OpenAI) | - |
| `ANTHROPIC_API_KEY` | Your Anthropic API key (if using Anthropic) | - |
| `GOOGLE_API_KEY` | Your Google API key (if using Google) | - |
| `LANGSMITH_TRACING` | Enable LangSmith tracing (optional) | `true` |
| `LANGSMITH_API_KEY` | Your LangSmith API key (optional) | - |
| `LANGSMITH_PROJECT` | Your LangSmith project name (optional) | `medical-chronology` |
