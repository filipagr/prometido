"""
backend/main.py

FastAPI app principal do Arquivo Eleitoral.
Serve os endpoints da API consumidos pelo frontend Next.js.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.database import init_db
from backend.api.search import router as search_router
from backend.api.parties import router as parties_router
from backend.api.promises import router as promises_router
from backend.api.elections import router as elections_router
from backend.api.compare import router as compare_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Arquivo Eleitoral API",
    description="O que prometeram. Onde está a prova.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://arquivoeleitoral.pt", "https://www.arquivoeleitoral.pt", "https://prometido-app.vercel.app"],
    # Aceita também previews do Vercel (frontend-*.vercel.app, *-filipagrs-projects.vercel.app, etc.)
    allow_origin_regex=r"https://([a-z0-9-]+\.)*vercel\.app",
    allow_methods=["GET"],
    allow_headers=["*"],
)

app.include_router(search_router, prefix="/api")
app.include_router(parties_router, prefix="/api")
app.include_router(promises_router, prefix="/api")
app.include_router(elections_router, prefix="/api")
app.include_router(compare_router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok", "project": "arquivo-eleitoral"}
