"""Tests for the extraction node."""

import os
from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from agent.models import MedChronoEvent
from agent.nodes.chunking import ChunkData
from agent.nodes.extract import extract_events


@pytest.fixture
def sample_chunk() -> ChunkData:
    """Create a sample chunk for testing."""
    return ChunkData(
        chunk_id=0,
        chunk_text="[Page 1]\nPatient visited clinic on 2024-01-15.\n[Page 2]\nDr. Smith performed evaluation.",
        start_page=1,
        end_page=22,
        total_pages=60,
    )


@pytest.fixture
def sample_event() -> MedChronoEvent:
    """Create a sample medical event for testing."""
    return MedChronoEvent(
        event_id="evt_001",
        date="2024-01-15",
        facility_name="General Hospital",
        doctor_name="Dr. Smith",
        event_type="consultation",
        event_summary="Patient visited clinic for evaluation",
        treatment="Clinical examination",
        citation_quote="Patient visited clinic on 2024-01-15 [p.1]",
        page=1,
        confidence_score=0.95,
        chunk_id=0,
        source_file="test.pdf",
        processing_timestamp=datetime.now(),
    )


def test_extract_events_returns_event_list(sample_chunk: ChunkData) -> None:
    """Test that extract_events returns a list of events."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        mock_response = """[{"event_id": "evt_mock", "date": "2024-01-15", "facility_name": "Test Hospital", "doctor_name": "Dr. Test", "event_type": "consultation", "event_summary": "Test summary", "treatment": "Test treatment", "citation_quote": "Test quote [p.1]", "page": 1, "confidence_score": 0.9, "chunk_id": 0, "source_file": "test.pdf", "processing_timestamp": "2024-01-01T00:00:00"}]"""

        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content=mock_response)
            mock_get_llm.return_value = mock_llm

            events = extract_events(sample_chunk, "test.pdf")

            assert isinstance(events, list)
            assert len(events) > 0
            assert isinstance(events[0], MedChronoEvent)


def test_extract_events_sets_metadata(sample_chunk: ChunkData) -> None:
    """Test that extract_events properly sets event metadata."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        mock_response = """[{"event_id": "evt_mock", "date": "2024-01-15", "facility_name": "Test Hospital", "doctor_name": "Dr. Test", "event_type": "consultation", "event_summary": "Test summary", "treatment": "Test treatment", "citation_quote": "Test quote [p.1]", "page": 1, "confidence_score": 0.9, "chunk_id": 999, "source_file": "wrong.pdf", "processing_timestamp": "2024-01-01T00:00:00"}]"""

        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content=mock_response)
            mock_get_llm.return_value = mock_llm

            events = extract_events(sample_chunk, "correct.pdf")

            assert len(events) == 1
            assert events[0].chunk_id == sample_chunk.chunk_id
            assert events[0].source_file == "correct.pdf"


def test_extract_events_generates_event_id_if_missing(sample_chunk: ChunkData) -> None:
    """Test that extract_events generates event_id if missing."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        mock_response = """[{"event_id": "", "date": "2024-01-15", "facility_name": "Test Hospital", "doctor_name": "Dr. Test", "event_type": "consultation", "event_summary": "Test summary", "treatment": "Test treatment", "citation_quote": "Test quote [p.1]", "page": 1, "confidence_score": 0.9, "chunk_id": 0, "source_file": "test.pdf", "processing_timestamp": "2024-01-01T00:00:00"}]"""

        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = MagicMock(content=mock_response)
            mock_get_llm.return_value = mock_llm

            events = extract_events(sample_chunk, "test.pdf")

            assert len(events) == 1
            assert events[0].event_id.startswith("evt_")
            assert len(events[0].event_id) == 12


def test_extract_events_with_retry_on_failure(sample_chunk: ChunkData) -> None:
    """Test that extract_events retries on LLM failure."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        mock_response = """[{"event_id": "evt_mock", "date": "2024-01-15", "facility_name": "Test Hospital", "doctor_name": "Dr. Test", "event_type": "consultation", "event_summary": "Test summary", "treatment": "Test treatment", "citation_quote": "Test quote [p.1]", "page": 1, "confidence_score": 0.9, "chunk_id": 0, "source_file": "test.pdf", "processing_timestamp": "2024-01-01T00:00:00"}]"""

        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = [
                Exception("API error"),
                Exception("API error"),
                MagicMock(content=mock_response),
            ]
            mock_get_llm.return_value = mock_llm

            events = extract_events(sample_chunk, "test.pdf")

            assert len(events) == 1
            assert mock_llm.invoke.call_count == 3


def test_extract_events_raises_after_max_attempts(sample_chunk: ChunkData) -> None:
    """Test that extract_events raises after max retry attempts."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.side_effect = Exception("Persistent API error")
            mock_get_llm.return_value = mock_llm

            with pytest.raises(Exception):
                extract_events(sample_chunk, "test.pdf")

            assert mock_llm.invoke.call_count == 3


def test_extract_events_handles_empty_chunk_text(sample_chunk: ChunkData) -> None:
    """Test that extract_events handles empty chunk text gracefully."""
    empty_chunk = ChunkData(
        chunk_id=1,
        chunk_text="",
        start_page=23,
        end_page=44,
        total_pages=60,
    )

    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = []
            mock_get_llm.return_value = mock_llm

            events = extract_events(empty_chunk, "test.pdf")

            assert isinstance(events, list)
            assert len(events) == 0


def test_extract_events_preserves_event_type_validation(sample_chunk: ChunkData) -> None:
    """Test that extract_events validates event types."""
    with patch.dict(
        os.environ,
        {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "test-key"},
    ):
        with patch("src.nodes.extract.get_structured_llm") as mock_get_llm:
            mock_llm = MagicMock()
            mock_llm.invoke.return_value = [
                {
                    "event_id": "evt_001",
                    "date": "2024-01-15",
                    "facility_name": "Hospital",
                    "doctor_name": "Dr. Smith",
                    "event_type": "invalid_type",
                    "event_summary": "Test",
                    "treatment": "Test",
                    "citation_quote": "Test [p.1]",
                    "page": 1,
                    "confidence_score": 0.9,
                    "chunk_id": 0,
                    "source_file": "test.pdf",
                    "processing_timestamp": datetime.now(),
                }
            ]
            mock_get_llm.return_value = mock_llm

            with pytest.raises(Exception):
                extract_events(sample_chunk, "test.pdf")
