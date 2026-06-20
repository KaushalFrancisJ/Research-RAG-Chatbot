import io
import os
from pypdf import PdfReader
from .text_chunker import chunk_pdf_metadata


def extract_pdf_content(source, filename: str = "document.pdf"):
    """
    Extract text from a PDF.

    `source` can be:
      - a file path (str) — used by the CLI / main.py batch processor
      - a bytes-like object or BytesIO — used by the API upload route (no disk I/O)
    """
    if isinstance(source, (bytes, bytearray)):
        source = io.BytesIO(source)

    reader = PdfReader(source)

    # Resolve a display name for the document
    title = (reader.metadata.title if reader.metadata else None) or filename

    page_content = []
    for page_num, page in enumerate(reader.pages):
        text_extract = page.extract_text() or ""
        text_extract = text_extract.replace("-\n", "").replace("\n", " ")
        text_extract = " ".join(text_extract.split())

        page_content.append({
            "page": page_num + 1,
            "text": text_extract,
            "images": [],          # image extraction skipped — not used by RAG pipeline
        })

    return page_content, title


def process_pdf(source, chunk_size=1000, overlap=200, filename: str = "document.pdf"):
    """
    Process a PDF and return chunks.

    `source` accepts the same types as extract_pdf_content:
    a file path string, raw bytes, or a BytesIO object.
    """
    if isinstance(source, str):
        filename = os.path.basename(source)
    page_content, title = extract_pdf_content(source, filename)
    return chunk_pdf_metadata(page_content, title, chunk_size, overlap)
