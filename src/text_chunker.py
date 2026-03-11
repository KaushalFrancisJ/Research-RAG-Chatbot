def chunk_pdf_metadata(pages_metadata, source, chunk_size=1000, overlap=200):
    doc_prefix = source.split('.')[0].lower().replace(" ", "_")
    chunks = []
    chunk_counter = 1

    for page_data in pages_metadata:
        page = page_data["page"]
        text = page_data["text"]
        images = page_data.get("images", [])

        text = text.replace("-\n", "").replace("\n", " ")
        text = " ".join(text.split())

        start = 0
        text_length = len(text)

        while start < text_length:
            end = start + chunk_size
            chunk_text = text[start:end]

            chunks.append({
                "chunk_id": f"{doc_prefix}_{chunk_counter}",
                "page": page,
                "text": chunk_text,
                "images": images,
                "source": source
            })

            chunk_counter += 1
            start += chunk_size - overlap

    return chunks
