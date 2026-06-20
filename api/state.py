from src.rag_pipeline import RAGPipeline
from config import EMBEDDING_MODEL

# Maps session_id -> RAGPipeline instance.
# Each browser session gets its own isolated index.
_sessions: dict[str, RAGPipeline] = {}


def get_session(session_id: str) -> RAGPipeline:
    """Return the RAGPipeline for this session, creating one if it doesn't exist."""
    if session_id not in _sessions:
        _sessions[session_id] = RAGPipeline(model_name=EMBEDDING_MODEL)
    return _sessions[session_id]


def clear_session(session_id: str) -> None:
    """Remove a session and free its memory."""
    _sessions.pop(session_id, None)
