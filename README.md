# Medical Chronology Extraction AI Workflow

AI workflow for extracting structured medical events from complex legal and medical PDF documents implemented with [LangGraph](https://langchain.com/langgraph), [Temporal.io](https://temporal.io) and [AWS Step Functions](https://aws.amazon.com/step-functions/).

## 🚀 Three Workflow Engines

This project provides three ways to run the medical chronology extraction:

1.  **LangGraph**: LangGraph is ideal for applications requiring AI agents to reason, plan, self-correct, and act autonomously, particularly when the workflow is conversational or cyclic.
2.  **Temporal**: Temporal is a "durable execution" engine, best for reliable, high-scale automation where workflows may run for minutes, hours, or months, requiring guaranteed completion despite infrastructure failures.
3.  **AWS Step Functions**: Step Functions is a visual state machine best suited for high-scale, serverless, event-driven architectures, particularly within the AWS ecosystem.

---

## 🎯 Choosing the Right Workflow Engine

### 1. LangGraph: Agentic AI & Human-in-the-Loop

**Best Use Cases:**

- **Complex Multi-Agent Systems**: Coordinating specialized agents (e.g., a "researcher" agent + "writer" agent + "critic" agent) that need to pass state back and forth
- **Conversational AI with Memory**: Building chatbots that require long-term memory across sessions, context management, and complex branching logic
- **Human-in-the-Loop (HITL)**: Scenarios where AI requires human approval or intervention to fix state (e.g., automated document editor with human review)
- **Self-Correcting Flows**: A loop where an agent proposes a solution, an evaluator critiques it, and it iterates until the quality requirement is met

**Why**: LangGraph offers cyclical graphs, persistent state, and deep integration with LangChain.

---

### 2. Temporal.io: Durable, Long-Running AI Agents

**Best Use Cases:**

- **Long-Running & Durable Agents**: Agents that need to wait for asynchronous external events (e.g., waiting 48 hours for a customer email reply)
- **Reliable Batch Processing**: Orchestrating thousands of LLM calls, handling automatic retries, rate limits, and compensation logic on failures
- **Multi-Cloud/Hybrid AI**: Orchestrating workflows that span on-premise infrastructure and multiple cloud providers
- **Mission-Critical Data Pipelines**: Using LLMs to process data, update databases, and manage state in real-time, such as content processing or data enrichment for LLMs

**Why**: Temporal allows code-first development (Python/TypeScript) and guarantees that a workflow resumes exactly where it left off after a crash.

---

### 3. AWS Step Functions: AWS-Native Serverless Orchestration

**Best Use Cases:**

- **Prompt Chaining in AWS**: Sequentially invoking Lambda functions, Bedrock models, or other services to process data
- **Visual Data Engineering (ETL)**: Creating, monitoring, and debugging complex ETL pipelines using Glue, Batch, and Lambda
- **AI/MLOps Pipelines**: Preprocessing data, training SageMaker models, and deploying them, with visual auditing for security and compliance
- **High-Volume/Express Workflows**: Short-duration, high-volume tasks (e.g., processing real-time user-uploaded files)

**Why**: Step Functions natively integrates with over 220 AWS services, provides visual debugging, and requires minimal infrastructure management.

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

The AWS engine uses **Amazon Step Functions** to orchestrate modular **AWS Lambda** functions. It leverages Google Gemini for AI processing, eliminating the need for external API keys and managing server infrastructure.

### 1. Configure AWS Secrets Manager
Create a secret in AWS Secrets Manager to store your LLM API key. The Lambda functions will use this to authenticate with the LLM provider's API, e.g. Google Gemini:

```bash
aws secretsmanager create-secret \
  --name medical-chrono/llm-api-key \
  --secret-string '{"key": "GOOGLE_API_KEY", "value":"your-actual-google-api-key"}'
```

The secret name and key structure (`medical-chrono/llm-api-key` with a `key` and `value` keys) are expected by the Lambda functions.

### 2. Build Lambda Packages
Use the build script to bundle the Python code and its dependencies into ZIP files (one for code, one for the Lambda Layer):
```bash
chmod +x scripts/build_lambda.sh
./scripts/build_lambda.sh
```

### 3. Deploy Infrastructure
Deploy the S3 buckets, Lambdas, IAM roles, and the Step Function using Terragrunt:
```bash
cd infra/live/dev
terragrunt apply-all
```

### 4. Trigger an Extraction
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
│   ├── graph.py              # LangGraph state machine definition
│   ├── models.py             # Structured Pydantic data models
│   ├── aws/                  # AWS Step Functions & Lambda handlers
│   │   ├── lambdas/          # Individual Lambda function entrypoints
│   │   └── s3_utils.py       # AWS S3 helper functions
│   ├── llm/                  # Provider abstraction & prompts
│   ├── nodes/                # Core AI logic (shared by all engines)
│   ├── temporal/             # Temporal-specific orchestration
│   │   ├── activities.py     # Temporal activity definitions
│   │   ├── workflow.py       # Temporal workflow definition
│   │   ├── worker.py         # Temporal worker implementation
│   │   └── run_workflow.py   # Workflow runner script
│   └── utils/                # PDF loading and utility helpers
├── infra/                    # Infrastructure as Code (Terraform + Terragrunt)
│   ├── live/                 # Terragrunt environment configurations
│   │   └── dev/              # Development environment
│   └── modules/              # Reusable Terraform modules
│       ├── lambda/           # Lambda function module
│       ├── s3/               # S3 bucket module
│       └── step_function/    # Step Function module
├── tests/                    # Comprehensive test suite
│   ├── samples/              # Test PDF samples
│   ├── temporal/             # Temporal-specific tests
│   ├── test_*.py             # Unit and integration tests
├── scripts/                  # Build and deployment utilities
│   └── build_lambda.sh       # Lambda package build script
├── samples/                  # Sample medical PDF documents
├── .env.example              # Environment variables template
├── pyproject.toml            # Python project configuration (uv)
├── langgraph.json            # LangGraph CLI configuration
└── docker-compose.yml        # Docker Compose for local infrastructure
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
