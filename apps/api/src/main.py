"""WrongAnswerBank API — 启动入口"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.config import settings
from src.routers import health, auth, mistakes, tts


@asynccontextmanager
async def lifespan(app: FastAPI):
    print(f"[wab-api] starting (env={settings.env})")
    yield
    print("[wab-api] shutting down")


app = FastAPI(
    title="WrongAnswerBank API",
    version="0.1.0",
    description="错题银行后端 API",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health.router, prefix="/api", tags=["health"])
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(mistakes.router, prefix="/api/mistakes", tags=["mistakes"])
app.include_router(tts.router, prefix="/api/tts", tags=["tts"])
