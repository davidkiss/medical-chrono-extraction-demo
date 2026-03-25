# Project Preferences - Medical Chronology Extraction Agent

## LangGraph Architecture (Map-Reduce)
- **Parallel Processing**: Always use a **conditional edge** (via `add_conditional_edges`) with a routing function to return `Send` objects.
- **Return Types**:
    - **Node functions** (added via `add_node`) MUST return a dictionary `dict` that updates the state.
    - **Routing functions** (used in `add_conditional_edges`) can return `Send` objects or destination node names.
- **State Aggregation**: Prefer using `Annotated[List[T], operator.add]` for automatic results merging in parallel branches to avoid redundant merge nodes.
- **Junctions**: When transitioning from a parallel phase (e.g., extraction) to another parallel phase (e.g., deduplication), always use a single intermediate "junction" node to allow all branches from the first phase to complete before fanning out for the second.

## Development Workflow
- **Package Manager**: Use `uv` for all dependency management and task execution.
- **Testing**: Use `pytest`. Run with `export PYTHONPATH=$PYTHONPATH:. && uv run pytest`.
- **Linting & Formatting**: Use `ruff`. Run with `uv run ruff check .` and `uv run ruff format .`.
- **Environment**: Load environment variables from `.env` using `dotenv`.

## Coding Standards
- **Pydantic**: Use Pydantic v2 for models and structured outputs.
- **Async**: Prefer async implementations when communicating with external LLM providers.
- **Error Handling**: Worker nodes (extract, dedup) should catch exceptions and return them in the `errors` list within the State to avoid stopping the entire graph.
