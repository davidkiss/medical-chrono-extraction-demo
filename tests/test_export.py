from datetime import datetime
import tempfile
import os
from agent.nodes.export import export_to_csv
from agent.models import MedChronoEvent

def test_export_creates_csv_with_headers():
    events = [
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
            processing_timestamp=datetime.now()
        )
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        csv_path = f.name
    
    export_to_csv(events, csv_path)
    
    with open(csv_path, 'r') as f:
        content = f.read()
    
    assert "event_id,date,facility_name,doctor_name,event_type" in content
    assert "evt_001" in content
    
    os.unlink(csv_path)

def test_export_sorts_by_date():
    events = [
        MedChronoEvent(
            event_id="evt_002",
            date="2024-01-16",
            facility_name="Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Test",
            treatment="Test",
            citation_quote="Quote [p.1]",
            page=1,
            confidence_score=0.95,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now()
        ),
        MedChronoEvent(
            event_id="evt_001",
            date="2024-01-15",
            facility_name="Hospital",
            doctor_name="Dr. Smith",
            event_type="procedure",
            event_summary="Test",
            treatment="Test",
            citation_quote="Quote [p.1]",
            page=1,
            confidence_score=0.95,
            chunk_id=0,
            source_file="test.pdf",
            processing_timestamp=datetime.now()
        )
    ]
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        csv_path = f.name
    
    export_to_csv(events, csv_path)
    
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    
    # evt_001 (2024-01-15) should come before evt_002 (2024-01-16)
    assert "evt_001" in lines[1]
    assert "evt_002" in lines[2]
    
    os.unlink(csv_path)
