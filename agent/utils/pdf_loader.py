import os

from pypdf import PdfReader


class PDFLoader:
    """PDF loader with page tracking support."""
    
    def load(self, pdf_path: str) -> str:
        """
        Load a PDF file and return text with page markers.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Text content with [Page N] markers for each page
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        reader = PdfReader(pdf_path)
        result = []
        
        for i, page in enumerate(reader.pages, start=1):
            page_text = page.extract_text() or ""
            result.append(f"[Page {i}]\n{page_text}")
        
        return "\n".join(result)
    
    def get_page_count(self, pdf_path: str) -> int:
        """
        Get the total page count of a PDF file.
        
        Args:
            pdf_path: Path to the PDF file
            
        Returns:
            Total number of pages
            
        Raises:
            FileNotFoundError: If the PDF file doesn't exist
        """
        if not pdf_path or not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        reader = PdfReader(pdf_path)
        return len(reader.pages)
