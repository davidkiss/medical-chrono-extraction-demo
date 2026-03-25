"""Pydantic models for medical chronology extraction."""

from dataclasses import dataclass
from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


@dataclass
class ChunkData:
    """Represents a PDF chunk for processing."""

    chunk_id: int
    chunk_text: str
    start_page: int
    end_page: int
    total_pages: int


class MedChronoEvent(BaseModel):
    """Represents a medical event extracted from legal documents."""

    event_id: str = Field(..., description="Unique identifier for the event")
    date: str | None = Field(None, description="Date of the medical event")
    facility_name: str | None = Field(None, description="Name of the medical facility")
    doctor_name: str | None = Field(None, description="Name of the treating doctor")
    event_type: Literal["procedure", "testing", "visit"] = Field(
        "visit", description="Type of medical event"
    )
    event_summary: str | None = Field(None, description="Brief summary of the event")
    treatment: str | None = Field(None, description="Treatment or procedure performed")
    citation_quote: str | None = Field(None, description="Original text quote from the document")
    page: int | None = Field(None, ge=1, description="Page number in the source document")
    confidence_score: float = Field(0.0, ge=0.0, le=1.0, description="Extraction confidence")
    chunk_id: int | None = Field(None, ge=0, description="Text chunk identifier")
    source_file: str | None = Field(None, description="Source document filename")
    processing_timestamp: datetime | None = Field(None, description="When the event was processed")

class MedChronoEventList(BaseModel):
    """List of medical events."""
    events: list[MedChronoEvent]

class DedupResult(BaseModel):
    """Represents a group of duplicate medical events."""
    duplicate_groups: list[list[str]] = Field(..., description="List of groups of duplicate event IDs")
    group_reasonings: list[str] = Field(..., description="Reasoning for each group")