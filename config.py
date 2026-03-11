import os

CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
OVERLAP = int(os.getenv('OVERLAP', 200))
PDF_DIR = os.getenv('PDF_DIR', '.\\pdfContext')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'dist')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
