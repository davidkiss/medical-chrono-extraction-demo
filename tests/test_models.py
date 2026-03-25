"""Tests for MedChronoEvent Pydantic model."""

from datetime import datetime
import pytest
from agent.models import MedChronoEvent


def test_med_chrono_event_creation():
    """Test that MedChronoEvent can be created with valid data."""
    event = MedChronoEvent(
        event_id="evt-001",
        date="2024-01-15",
        facility_name="General Hospital",
        doctor_name="Dr. Smith",
        event_type="procedure",
        event_summary="Patient underwent knee surgery",
        treatment="Arthroscopic meniscus repair",
        citation_quote="The patient was admitted for knee surgery on January 15, 2024",
        page=5,
        confidence_score=0.95,
        chunk_id=12,
        source_file="medical_record.pdf",
        processing_timestamp=datetime(2024, 1, 20, 10, 30, 0),
    )

    assert event.event_id == "evt-001"
    assert event.date == "2024-01-15"
    assert event.facility_name == "General Hospital"
    assert event.doctor_name == "Dr. Smith"
    assert event.event_type == "procedure"
    assert event.event_summary == "Patient underwent knee surgery"
    assert event.treatment == "Arthroscopic meniscus repair"
    assert event.citation_quote == "The patient was admitted for knee surgery on January 15, 2024"
    assert event.page == 5
    assert event.confidence_score == 0.95
    assert event.chunk_id == 12
    assert event.source_file == "medical_record.pdf"
    assert event.processing_timestamp == datetime(2024, 1, 20, 10, 30, 0)


def test_confidence_score_bounds():
    """Test that confidence_score is bounded between 0.0 and 1.0."""
    # Valid boundary values
    event_min = MedChronoEvent(
        event_id="evt-002",
        date="2024-01-15",
        facility_name="General Hospital",
        doctor_name="Dr. Smith",
        event_type="procedure",
        event_summary="Test",
        treatment="Test",
        citation_quote="Test",
        page=1,
        confidence_score=0.0,
        chunk_id=0,
        source_file="test.pdf",
        processing_timestamp=datetime.now(),
    )
    assert event_min.confidence_score == 0.0

    event_max = MedChronoEvent(
        event_id="evt-003",
        date="2024-01-15",
        facility_name="General Hospital",
        doctor_name="Dr. Smith",
        event_type="procedure",
        event_summary="Test",
        treatment="Test",
        citation_quote="Test",
        page=1,
        confidence_score=1.0,
        chunk_id=0,
        source_file="test.pdf",
        processing_timestamp=datetime.now(),
    )
    assert event_max.confidence_score == 1.0

    # Invalid values should raise ValidationError
    with pytest.raises(Exception):
        MedChronoEvent(
            event_id="evt-004",
            date="2024-01-15",
            facility_name="General Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Test",
            treatment="Test",
            citation_quote="Test",
            page=1,
            confidence_score=-0.1,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        )

    with pytest.raises(Exception):
        MedChronoEvent(
            event_id="evt-005",
            date="2024-01-15",
            facility_name="General Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Test",
            treatment="Test",
            citation_quote="Test",
            page=1,
            confidence_score=1.1,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        )


def test_invalid_event_type():
    """Test that invalid event_type raises ValidationError."""
    with pytest.raises(Exception):
        MedChronoEvent(
            event_id="evt-006",
            date="2024-01-15",
            facility_name="General Hospital",
            doctor_name="Dr. Smith",
            event_type="surgery",
            event_summary="Test",
            treatment="Test",
            citation_quote="Test",
            page=1,
            confidence_score=0.5,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now(),
        )
