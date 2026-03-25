"""Tests for PDF chunking strategy."""

from agent.nodes.chunking import create_chunks, ChunkData, extract_page_range


def test_create_chunks_generates_correct_ranges():
    """For a 60-page document: chunks are 1-22, 21-42, 41-60."""
    full_text = ""
    for i in range(1, 61):
        full_text += f"[Page {i}]\nContent {i}\n"
    
    chunks = create_chunks(full_text=full_text, total_pages=60, chunk_size=20, overlap=2)
    assert len(chunks) == 3
    assert chunks[0].start_page == 1
    assert chunks[0].end_page == 22
    assert chunks[1].start_page == 21
    assert chunks[1].end_page == 42
    assert chunks[2].start_page == 41
    assert chunks[2].end_page == 60


def test_chunk_data_has_required_fields():
    """Verify ChunkData has all required fields."""
    full_text = "[Page 1]\nContent"
    chunks = create_chunks(full_text=full_text, total_pages=30, chunk_size=20, overlap=2)
    assert len(chunks) == 2
    assert chunks[0].chunk_id == 0
    assert isinstance(chunks[0].start_page, int)
    assert isinstance(chunks[0].end_page, int)
    assert chunks[0].start_page == 1
    assert chunks[0].end_page == 22


def test_overlap_pages_are_included():
    """Chunk 0: pages 1-22, Chunk 1: pages 21-42. Pages 21-22 should overlap."""
    full_text = ""
    for i in range(1, 51):
        full_text += f"[Page {i}]\nContent\n"
    chunks = create_chunks(full_text=full_text, total_pages=50, chunk_size=20, overlap=2)
    assert chunks[0].end_page == 22
    assert chunks[1].start_page == 21


def test_extract_page_range_extractors_correct_pages():
    """Test extract_page_range helper function."""
    full_text = "[Page 1]\nContent 1\n[Page 2]\nContent 2\n[Page 3]\nContent 3"
    result = extract_page_range(full_text, 1, 2)
    assert "[Page 1]" in result
    assert "[Page 2]" in result
    assert "[Page 3]" not in result
    assert "Content 1" in result
    assert "Content 2" in result


def test_create_chunks_with_small_document():
    """Test chunking with document smaller than chunk size."""
    chunks = create_chunks(full_text="[Page 1]\nContent", total_pages=10, chunk_size=20, overlap=2)
    assert len(chunks) == 1
    assert chunks[0].start_page == 1
    assert chunks[0].end_page == 10


def test_chunk_data_dataclass_fields():
    """Verify ChunkData dataclass has all required fields."""
    chunk = ChunkData(
        chunk_id=0, chunk_text="test content", start_page=1, end_page=22, total_pages=60
    )
    assert chunk.chunk_id == 0
    assert chunk.chunk_text == "test content"
    assert chunk.start_page == 1
    assert chunk.end_page == 22
    assert chunk.total_pages == 60
