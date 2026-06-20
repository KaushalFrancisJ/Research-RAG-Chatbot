from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes.upload import router as upload_router
from api.routes.generate import router as generate_router
from api.routes.evaluate import router as evaluate_router
from api import state


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Server is starting up — nothing to initialise yet
    yield
    # Server is shutting down — release all in-memory session data
    state._sessions.clear()


app = FastAPI(title="RAG API", lifespan=lifespan)

app.include_router(upload_router, prefix="/api")
app.include_router(generate_router, prefix="/api")
app.include_router(evaluate_router, prefix="/api")
