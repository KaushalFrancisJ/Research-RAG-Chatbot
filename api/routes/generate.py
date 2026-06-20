from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel
from src.generator import generate
from api.state import get_session

router = APIRouter()


class GenerateRequest(BaseModel):
    query: str
    k: int = 5


@router.post("/generate")
def generate_answer(
    req: GenerateRequest,
    x_session_id: str = Header(..., alias="X-Session-Id"),
):
    rag = get_session(x_session_id)

    if not rag.vector_store:
        raise HTTPException(status_code=400, detail="No index found. Upload a PDF first.")

    results = rag.query(req.query, k=req.k)
    context = "\n\n".join(r["chunk"]["text"] for r in results)
    answer = generate(req.query, context)

    return {
        "query": req.query,
        "answer": answer,
        "chunks": [
            {"text": r["chunk"]["text"], "source": r["chunk"]["source"], "page": r["chunk"]["page"]}
            for r in results
        ],
    }
