import re

# Priority order of separators: paragraph → sentence → word → character
_SEPARATORS = ["\n\n", "\n", r"(?<=[.!?])\s+", r"\s+", ""]


def _split_by_separator(text: str, separator: str) -> list[str]:
    """Split text by a separator (supports regex)."""
    if separator == "":
        # character-level fallback: split into individual chars
        return list(text)
    return re.split(separator, text)


def _recursive_split(text: str, chunk_size: int, separators: list[str]) -> list[str]:
    """
    Recursively split text using the first separator that produces pieces
    small enough to fit within chunk_size. Falls back to the next separator
    when a piece is still too large.
    """
    # Base case: text already fits
    if len(text) <= chunk_size:
        return [text]

    separator = separators[0]
    remaining = separators[1:]

    pieces = _split_by_separator(text, separator)

    result = []
    for piece in pieces:
        piece = piece.strip()
        if not piece:
            continue
        if len(piece) <= chunk_size:
            result.append(piece)
        elif remaining:
            # piece still too large — recurse with the next separator
            result.extend(_recursive_split(piece, chunk_size, remaining))
        else:
            # no more separators — hard-cut at chunk_size
            for i in range(0, len(piece), chunk_size):
                result.append(piece[i : i + chunk_size])

    return result


def _merge_with_overlap(pieces: list[str], chunk_size: int, overlap: int) -> list[str]:
    """
    Merge small pieces into chunks up to chunk_size, then carry the last
    `overlap` characters forward into the next chunk so context is preserved
    across boundaries.
    """
    chunks: list[str] = []
    current = ""

    for piece in pieces:
        candidate = (current + " " + piece).strip() if current else piece

        if len(candidate) <= chunk_size:
            current = candidate
        else:
            # Flush the current chunk
            if current:
                chunks.append(current)
            # Start new chunk: seed it with the overlap tail of the previous chunk
            if chunks:
                overlap_seed = chunks[-1][-overlap:] if overlap > 0 else ""
                current = (overlap_seed + " " + piece).strip() if overlap_seed else piece
            else:
                current = piece

    if current:
        chunks.append(current)

    return chunks


def chunk_pdf_metadata(pages_metadata: list[dict], source: str,
                       chunk_size: int = 1000, overlap: int = 200) -> list[dict]:
    """
    Split each page's text using recursive splitting (paragraph → sentence →
    word → character) with overlap between chunks.

    Returns a list of chunk dicts compatible with the rest of the pipeline.
    """
    doc_prefix = source.split(".")[0].lower().replace(" ", "_")
    chunks: list[dict] = []
    chunk_counter = 1

    for page_data in pages_metadata:
        page = page_data["page"]
        text = page_data["text"]
        images = page_data.get("images", [])

        # Normalise whitespace but preserve paragraph/sentence boundaries
        text = text.replace("-\n", "")           # rejoin hyphenated line breaks
        text = re.sub(r"\n{3,}", "\n\n", text)   # collapse excessive blank lines
        text = re.sub(r"[ \t]+", " ", text).strip()

        if not text:
            continue

        # 1. Recursively split into natural pieces
        pieces = _recursive_split(text, chunk_size, _SEPARATORS)

        # 2. Merge small pieces and apply overlap
        page_chunks = _merge_with_overlap(pieces, chunk_size, overlap)

        for chunk_text in page_chunks:
            chunk_text = chunk_text.strip()
            if not chunk_text:
                continue
            chunks.append({
                "chunk_id": f"{doc_prefix}_{chunk_counter}",
                "page": page,
                "text": chunk_text,
                "images": images,
                "source": source,
            })
            chunk_counter += 1

    return chunks
