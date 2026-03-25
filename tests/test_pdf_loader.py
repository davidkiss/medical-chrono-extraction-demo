import pytest
from agent.utils.pdf_loader import PDFLoader


def test_load_returns_text_with_page_markers():
    """Test that load() returns text with [Page N] markers for each page."""
    pdf_path = "samples/sample-medical-chronology.pdf"
    loader = PDFLoader()
    
    text = loader.load(pdf_path)
    
    assert text is not None
    assert "[Page 1]" in text


def test_load_raises_filenoterror_for_nonexistent_file():
    """Test that load() raises FileNotFoundError if PDF doesn't exist."""
    loader = PDFLoader()
    
    with pytest.raises(FileNotFoundError):
        loader.load("nonexistent_file.pdf")
