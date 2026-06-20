from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes.upload import router as upload_router
from api.routes.generate import router as generate_router
from api.routes.evaluate import router as evaluate_router
from api import state
from config import ALLOWED_ORIGINS


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    state._sessions.clear()


app = FastAPI(title="RAG API", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
app.include_router(evaluate_router, prefix="/api")
