import tempfile
import os
from pathlib import Path
import pytest
from agent.graph import create_extraction_graph

def test_e2e_with_sample_pdf(monkeypatch):
    """
    End-to-end test of the extraction graph.
    Requires a sample PDF in samples/sample.pdf.
    """
    monkeypatch.setenv("LLM_PROVIDER", "openai")
    monkeypatch.setenv("OPENAI_API_KEY", "test-key")
    
    # Check if sample PDF exists, otherwise skip
    pdf_path = "samples/sample-medical-chronology.pdf"
    if not os.path.exists(pdf_path):
        pytest.skip(f"Sample PDF {pdf_path} not found")
        
    graph = create_extraction_graph()
    
    with tempfile.NamedTemporaryFile(suffix='.csv', delete=False) as f:
        csv_path = f.name
    
    state = {
        'pdf_path': pdf_path,
        'chunks': [],
        'results': [],
        'errors': [],
        'csv_output_path': csv_path,
        'all_events': []
    }
    
    # Note: This will attempt to call actual LLM if not mocked.
    # In a real CI environment, we would mock the LLM provider.
    # For this test, we'll just verify the graph can be invoked 
    # and handles basic state setup.
    
    # Since we don't have a real API key, we expect this might fail 
    # or we should mock the nodes.
    # But Task 13 in the breakdown suggests running it.
    
    import unittest.mock as mock
    
    # Mock the nodes to avoid real API calls
    with mock.patch("src.graph.extract_events") as mock_extract:
        from src.models import MedChronoEvent
        from datetime import datetime
        
        mock_extract.return_value = [
            MedChronoEvent(
                event_id="evt_001",
                date="2024-01-15",
                facility_name="Test Clinic",
                doctor_name="Dr. Test",
                event_type="consultation",
                event_summary="Test Summary",
                treatment="None",
                citation_quote="Quote [p.1]",
                page=1,
                confidence_score=1.0,
                chunk_id=0,
                source_file="sample-medical-chronology.pdf",
                processing_timestamp=datetime.now()
            )
        ]
        
        with mock.patch("src.graph.deduplicate_events_by_date") as mock_dedup:
            mock_dedup.side_effect = lambda x: x  # Pass through
            
            result = graph.invoke(state)
    
    # Assert CSV created
    assert os.path.exists(csv_path)
    
    # Assert CSV has content
    with open(csv_path, 'r') as f:
        lines = f.readlines()
    assert len(lines) > 1  # Header + at least one event
    
    # Assert expected columns
    header = lines[0]
    assert 'event_id' in header
    assert 'date' in header
    assert 'facility_name' in header
    
    os.unlink(csv_path)
