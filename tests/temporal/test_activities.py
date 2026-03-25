import pytest
from unittest.mock import MagicMock, patch
from agent.temporal.activities import extract_chunk_activity, load_and_chunk_pdf_activity
from agent.models import ChunkData, MedChronoEvent

@pytest.mark.asyncio
async def test_extract_chunk_activity_calls_extract_events():
    # Setup mock
    chunk = ChunkData(chunk_id=0, chunk_text="test", start_page=1, end_page=1, total_pages=1)
    pdf_path = "test.pdf"
    mock_events = [MedChronoEvent(event_id="evt_123", date="2024-01-01", event_type="visit", event_summary="test")]
    
    with patch("agent.temporal.activities.extract_events", return_value=mock_events) as mock_extract:
        result = await extract_chunk_activity({"chunk": chunk, "pdf_path": pdf_path})
        
        mock_extract.assert_called_once_with(chunk, pdf_path)
        assert result == mock_events

@pytest.mark.asyncio
async def test_load_and_chunk_pdf_activity_orchestrates_logic():
    # Setup mocks
    pdf_path = "test.pdf"
    mock_text = "full text"
    mock_pages = 10
    mock_chunks = [ChunkData(chunk_id=0, chunk_text="chunk 0", start_page=1, end_page=5, total_pages=10)]
    
    with patch("agent.temporal.activities.PDFLoader") as MockLoader, \
         patch("agent.temporal.activities.create_chunks", return_value=mock_chunks) as mock_create_chunks:
        
        # Configure loader mock
        loader_instance = MockLoader.return_value
        loader_instance.load.return_value = mock_text
        loader_instance.get_page_count.return_value = mock_pages
        
        result = await load_and_chunk_pdf_activity(pdf_path)
        
        loader_instance.load.assert_called_once_with(pdf_path)
        loader_instance.get_page_count.assert_called_once_with(pdf_path)
        mock_create_chunks.assert_called_once()
        assert result == mock_chunks
