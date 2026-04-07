"""Tests for deduplication node."""

from datetime import datetime
from unittest.mock import MagicMock, patch

import pytest

from agent.models import MedChronoEvent
from agent.nodes.dedup import deduplicate_events_by_date


@pytest.fixture
def sample_events_same_date() -> list[MedChronoEvent]:
    """Create sample events with same date for deduplication testing."""
    return [
        MedChronoEvent(
            event_id="evt_001",
            date="2024-01-15",
            facility_name="General Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Cardiac evaluation",
            treatment="EKG",
            citation_quote="Quote 1 [p.5]",
            page=5,
            confidence_score=0.95,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        ),
        MedChronoEvent(
            event_id="evt_002",
            date="2024-01-15",
            facility_name="General Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Cardiac evaluation",
            treatment="EKG",
            citation_quote="Quote 2 [p.6]",
            page=6,
            confidence_score=0.90,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_events_different_dates() -> list[MedChronoEvent]:
    """Create sample events with different dates."""
    return [
        MedChronoEvent(
            event_id="evt_001",
            date="2024-01-15",
            facility_name="Hospital A",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Procedure A",
            treatment="Treatment A",
            citation_quote="Quote [p.1]",
            page=1,
            confidence_score=0.95,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        ),
        MedChronoEvent(
            event_id="evt_002",
            date="2024-01-16",
            facility_name="Hospital B",
            doctor_name="Dr. Jones",
            event_type="testing",
            event_summary="Test B",
            treatment="Treatment B",
            citation_quote="Quote [p.2]",
            page=2,
            confidence_score=0.90,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        ),
    ]


@pytest.fixture
def sample_events_unique_same_date() -> list[MedChronoEvent]:
    """Create sample unique events on same date (different facilities/doctors)."""
    return [
        MedChronoEvent(
            event_id="evt_001",
            date="2024-01-15",
            facility_name="Hospital A",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Procedure A",
            treatment="Treatment A",
            citation_quote="Quote [p.1]",
            page=1,
            confidence_score=0.95,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        ),
        MedChronoEvent(
            event_id="evt_002",
            date="2024-01-15",
            facility_name="Hospital B",
            doctor_name="Dr. Jones",
            event_type="testing",
            event_summary="Test B",
            treatment="Treatment B",
            citation_quote="Quote [p.2]",
            page=2,
            confidence_score=0.90,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        ),
    ]


@pytest.fixture
def single_event() -> list[MedChronoEvent]:
    """Create a single event list."""
    return [
        MedChronoEvent(
            event_id="evt_001",
            date="2024-01-15",
            facility_name="General Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Cardiac evaluation",
            treatment="EKG",
            citation_quote="Quote [p.5]",
            page=5,
            confidence_score=0.95,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        )
    ]


@patch("agent.nodes.dedup.get_structured_llm")
def test_dedup_removes_duplicates(
    mock_get_llm_client: MagicMock, sample_events_same_date: list[MedChronoEvent]
) -> None:
    """Test that deduplication removes duplicate events."""
    # Mock LLM to return duplicate groups
    from agent.models import DedupResult
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = DedupResult(
        duplicate_groups=[["evt_001", "evt_002"]],
        group_reasonings=["Same event"]
    )
    mock_get_llm_client.return_value = mock_llm

    deduped = deduplicate_events_by_date(sample_events_same_date)
    assert len(deduped) == 1
    assert deduped[0].event_id == "evt_001"


def test_dedup_keeps_unique_events_different_dates(
    sample_events_different_dates: list[MedChronoEvent],
) -> None:
    """Test that events on different dates are kept."""
    deduped = deduplicate_events_by_date(sample_events_different_dates)
    assert len(deduped) == 2
    event_ids = {evt.event_id for evt in deduped}
    assert "evt_001" in event_ids
    assert "evt_002" in event_ids


@patch("agent.nodes.dedup.get_structured_llm")
def test_dedup_keeps_unique_events_same_date(
    mock_get_llm_client: MagicMock, sample_events_unique_same_date: list[MedChronoEvent]
) -> None:
    """Test that unique events on same date are kept."""
    # Mock LLM to return empty duplicate groups (no duplicates)
    from agent.models import DedupResult
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = DedupResult(
        duplicate_groups=[],
        group_reasonings=[]
    )
    mock_get_llm_client.return_value = mock_llm

    deduped = deduplicate_events_by_date(sample_events_unique_same_date)
    assert len(deduped) == 2
    event_ids = {evt.event_id for evt in deduped}
    assert "evt_001" in event_ids
    assert "evt_002" in event_ids


def test_dedup_single_event(single_event: list[MedChronoEvent]) -> None:
    """Test that single event is returned unchanged."""
    deduped = deduplicate_events_by_date(single_event)
    assert len(deduped) == 1
    assert deduped[0].event_id == "evt_001"


def test_dedup_empty_list() -> None:
    """Test that empty list returns empty list."""
    deduped = deduplicate_events_by_date([])
    assert len(deduped) == 0


@patch("agent.nodes.dedup.get_structured_llm")
def test_dedup_preserves_event_data(
    mock_get_llm_client: MagicMock, sample_events_same_date: list[MedChronoEvent]
) -> None:
    """Test that preserved event data is unchanged."""
    # Mock LLM to return duplicate groups
    from agent.models import DedupResult
    mock_llm = MagicMock()
    mock_llm.invoke.return_value = DedupResult(
        duplicate_groups=[["evt_001", "evt_002"]],
        group_reasonings=["Same event"]
    )
    mock_get_llm_client.return_value = mock_llm

    deduped = deduplicate_events_by_date(sample_events_same_date)
    assert len(deduped) == 1
    assert deduped[0].event_id == "evt_001"
    assert deduped[0].facility_name == "General Hospital"
    assert deduped[0].doctor_name == "Dr. Smith"
    assert deduped[0].event_type == "procedure"
