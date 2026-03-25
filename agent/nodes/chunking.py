"""PDF chunking strategy for medical chronology extraction."""

from agent.models import ChunkData

def create_chunks(
    full_text: str, total_pages: int, chunk_size: int = 20, overlap: int = 2
) -> list[ChunkData]:
    """
    Create chunks with specified overlap.

    Pattern: 1-22, 20-42, 40-62, etc. (20 new pages + 2 overlap)

    Args:
        full_text: Full PDF text with [Page N] markers
        total_pages: Total number of pages in the document
        chunk_size: Number of new pages per chunk (default 20)
        overlap: Number of overlapping pages (default 2)

    Returns:
        List of ChunkData objects
    """
    chunks = []
    chunk_id = 0
    current_start = 1

    while current_start <= total_pages:
        current_end = min(current_start + chunk_size + overlap - 1, total_pages)

        # Extract chunk text by finding page markers
        chunk_text = extract_page_range(full_text, current_start, current_end)

        chunks.append(
            ChunkData(
                chunk_id=chunk_id,
                chunk_text=chunk_text,
                start_page=current_start,
                end_page=current_end,
                total_pages=total_pages,
            )
        )

        chunk_id += 1
        # Move start forward by chunk_size (not chunk_size + overlap)
        current_start = current_start + chunk_size

        if current_start > total_pages:
            break

    return chunks


def extract_page_range(full_text: str, start_page: int, end_page: int) -> str:
    """
    Extract text for a specific page range from full PDF text.

    Args:
        full_text: Full PDF text with [Page N] markers
        start_page: Starting page number (1-indexed)
        end_page: Ending page number (inclusive)

    Returns:
        Extracted text for the specified page range
    """
    lines = full_text.split("\n")
    chunk_lines = []
    in_range = False

    for line in lines:
        if line.startswith("[Page"):
            page_num = int(line.split("]")[0].replace("[Page ", "").strip())
            if start_page <= page_num <= end_page:
                in_range = True
            elif page_num > end_page:
                in_range = False
                break

        if in_range:
            chunk_lines.append(line)

    return "\n".join(chunk_lines)
