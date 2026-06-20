from fastapi import APIRouter, Header, HTTPException
from src.evaluator import evaluate
from src.generator import generate
from api.state import get_session

router = APIRouter()

# Fixed diagnostic questions used to probe RAG quality regardless of the document.
# They are intentionally open-ended so they work against any indexed PDF.
EVAL_QUESTIONS = [
    "What is the main topic of this document?",
    "Summarise the key findings or conclusions.",
    "What problem does this document address?",
    "What methods or approaches are described?",
    "What are the limitations mentioned in this document?",
]


@router.post("/evaluate")
def evaluate_rag(
    x_session_id: str = Header(..., alias="X-Session-Id"),
):
    rag = get_session(x_session_id)

    if not rag.vector_store:
        raise HTTPException(status_code=400, detail="No index found. Upload a PDF first.")

    results = []
    for question in EVAL_QUESTIONS:
        retrieved = rag.query(question, k=5)
        context = "\n\n".join(r["chunk"]["text"] for r in retrieved)
        answer = generate(question, context)
        scores = evaluate(question, context, answer)

        results.append({
            "question": question,
            "answer": answer,
            "faithfulness": scores["faithfulness"],
            "faithfulness_reason": scores["faithfulness_reason"],
            "answer_relevancy": scores["answer_relevancy"],
            "answer_relevancy_reason": scores["answer_relevancy_reason"],
        })

    return {"results": results}
