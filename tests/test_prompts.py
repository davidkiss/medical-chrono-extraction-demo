"""Tests for LLM prompts."""

from agent.llm.prompts import EXTRACTION_PROMPT, DEDUP_PROMPT, EVENT_TYPE_DEFINITIONS


def test_extraction_prompt_contains_event_types() -> None:
    """Test that extraction prompt contains all event type definitions."""
    assert "procedure" in EXTRACTION_PROMPT
    assert "testing" in EXTRACTION_PROMPT
    assert "consultation" in EXTRACTION_PROMPT


def test_extraction_prompt_contains_field_instructions() -> None:
    """Test that extraction prompt contains required field instructions."""
    assert "date" in EXTRACTION_PROMPT
    assert "facility_name" in EXTRACTION_PROMPT
    assert "citation_quote" in EXTRACTION_PROMPT


def test_dedup_prompt_contains_json_format() -> None:
    """Test that dedup prompt mentions JSON format."""
    assert "JSON" in DEDUP_PROMPT or "json" in DEDUP_PROMPT


def test_event_type_definitions_complete() -> None:
    """Test that event type definitions include all three types."""
    assert "procedure" in EVENT_TYPE_DEFINITIONS
    assert "testing" in EVENT_TYPE_DEFINITIONS
    assert "consultation" in EVENT_TYPE_DEFINITIONS
