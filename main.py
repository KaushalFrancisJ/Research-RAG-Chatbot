import os
import glob
from src.pdf_processor import process_pdf
from src.rag_pipeline import RAGPipeline
from config import CHUNK_SIZE, OVERLAP, PDF_DIR, EMBEDDING_MODEL

def process_all_pdfs(pdf_dir=PDF_DIR, chunk_size=CHUNK_SIZE, overlap=OVERLAP):
    pdf_files = glob.glob(os.path.join(pdf_dir, '*.pdf'))
    
    if not pdf_files:
        print(f"No PDF files found in {pdf_dir}")
        return []
    
    all_chunks = []
    for pdf_path in pdf_files:
        print(f"Processing: {os.path.basename(pdf_path)}")
        chunks = process_pdf(pdf_path, chunk_size=chunk_size, overlap=overlap)
        all_chunks.extend(chunks)
    
    return all_chunks

if __name__ == "__main__":
    print("Step 1: Processing PDFs...")
    chunks = process_all_pdfs()
    print(f"Total chunks created: {len(chunks)}")
    
    if chunks:
        print(f"\nStep 2: Building embeddings and index...")
        rag = RAGPipeline(model_name=EMBEDDING_MODEL)
        rag.build_index(chunks)
        print(f"Index built with {len(chunks)} chunks")
        
        print(f"\nStep 3: Testing query...")
        query = "What is Memory Caching?"
        results = rag.query(query, k=5)
        
        print(f"\nQuery: {query}")
        print(f"Top {len(results)} results:")
        for i, result in enumerate(results, 1):
            chunk = result["chunk"]
            print(f"\n{i}. [Distance: {result['distance']:.4f}]")
            print(f"   Source: {chunk['source']} (Page {chunk['page']})")
            print(f"   Text: {chunk['text'][:150]}...")
