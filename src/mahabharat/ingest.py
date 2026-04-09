"""PDF ingestion and text chunking."""
import fitz  # PyMuPDF
from typing import List, Dict
from .config import PDF_PATH, CHUNK_SIZE, CHUNK_OVERLAP


def load_pdf(path: str = PDF_PATH) -> List[Dict]:
    """Extract text from PDF, return list of page dicts."""
    doc = fitz.open(path)
    pages = []
    for i, page in enumerate(doc):
        text = page.get_text()
        if text.strip():
            pages.append({"page": i + 1, "text": text})
    doc.close()
    print(f"Loaded {len(pages)} pages from {path}")
    return pages


def chunk_pages(pages: List[Dict]) -> List[Dict]:
    """Sliding-window chunking over concatenated page text."""
    # Concatenate all text with page markers
    full_text = ""
    page_offsets = []  # (char_offset, page_num)
    for p in pages:
        page_offsets.append((len(full_text), p["page"]))
        full_text += p["text"] + "\n\n"

    chunks = []
    start = 0
    chunk_id = 0
    while start < len(full_text):
        end = start + CHUNK_SIZE
        text = full_text[start:end]

        # Find which page this chunk starts on
        page_num = 1
        for offset, pnum in page_offsets:
            if offset <= start:
                page_num = pnum

        chunks.append({
            "id": chunk_id,
            "text": text,
            "start_page": page_num,
            "char_start": start,
        })
        chunk_id += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP

    print(f"Created {len(chunks)} chunks")
    return chunks
