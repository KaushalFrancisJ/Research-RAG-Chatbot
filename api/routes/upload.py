from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from config import CHUNK_SIZE, OVERLAP
from src.pdf_processor import process_pdf
from api.state import get_session

router = APIRouter()


@router.post("/upload")
async def upload_and_chunk(
    file: UploadFile = File(...),
    x_session_id: str = Header(..., alias="X-Session-Id"),
):
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    # Read entirely into memory — no disk writes
    pdf_bytes = await file.read()

    rag = get_session(x_session_id)
    chunks = process_pdf(pdf_bytes, chunk_size=CHUNK_SIZE, overlap=OVERLAP, filename=file.filename)
    rag.build_index(chunks)

    return {"filename": file.filename, "chunks": len(chunks)}
