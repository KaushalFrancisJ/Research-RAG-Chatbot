from src.main import process_all_pdfs

if __name__ == "__main__":
    chunks = process_all_pdfs()
    print(f"\nTotal chunks: {len(chunks)}")
    if chunks:
        print(f"Sample chunk:\n{chunks[0]}")