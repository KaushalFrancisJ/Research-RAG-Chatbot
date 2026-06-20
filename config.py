import os
from dotenv import load_dotenv

load_dotenv()

ENV = os.getenv('ENV', 'local')
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
OVERLAP = int(os.getenv('OVERLAP', 200))
PDF_DIR = os.getenv('PDF_DIR', '.\\pdfContext')
OUTPUT_DIR = os.getenv('OUTPUT_DIR', 'dist')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'all-MiniLM-L6-v2')
GENERATION_MODEL = os.getenv('GENERATION_MODEL', 'mistral:7b-instruct-q4_0')
GROQ_GENERATION_MODEL = os.getenv('GROQ_GENERATION_MODEL', 'llama-3.3-70b-versatile')
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
EVALUATION_MODEL = os.getenv('EVALUATION_MODEL', 'llama-3.3-70b-versatile')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')
ALLOWED_ORIGINS = os.getenv('ALLOWED_ORIGINS', 'http://localhost:8501').split(',')
