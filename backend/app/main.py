from collections.abc import AsyncGenerator
from pathlib import Path
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from app.config import settings
from app.database import engine, Base, SessionLocal
from app.errors import INTERNAL_SERVER_ERROR
from app.routers import game, auth
from app.services.game_service import abandon_stale_games
import app.models  # noqa: F401

FRONTEND_DIR = Path(__file__).parent.parent.parent / "frontend"
if not FRONTEND_DIR.exists():
    FRONTEND_DIR = Path("/app/frontend")


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[None, None]:
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        abandon_stale_games(db)
    finally:
        db.close()
    yield


app = FastAPI(
    title=settings.app_title,
    description=settings.app_description,
    version=settings.app_version,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=settings.cors_allow_methods,
    allow_headers=settings.cors_allow_headers,
)

_STATUS_TITLES: dict[int, str] = {
    400: "Requisição Inválida",
    401: "Não Autenticado",
    403: "Acesso Negado",
    404: "Não Encontrado",
    422: "Erro de Validação",
    500: "Erro Interno",
}


def _status_title(code: int) -> str:
    return _STATUS_TITLES.get(code, "Erro")


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for error in exc.errors():
        field = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        errors.append(f"{field}: {error['msg']}" if field else error["msg"])
    return JSONResponse(
        status_code=422,
        content={
            "type": "about:blank",
            "title": _status_title(422),
            "status": 422,
            "detail": errors,
            "instance": str(request.url.path),
        },
        media_type="application/problem+json",
    )


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "type": "about:blank",
            "title": _status_title(exc.status_code),
            "status": exc.status_code,
            "detail": exc.detail,
            "instance": str(request.url.path),
        },
        media_type="application/problem+json",
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    return JSONResponse(
        status_code=500,
        content={
            "type": "about:blank",
            "title": _status_title(500),
            "status": 500,
            "detail": INTERNAL_SERVER_ERROR,
            "instance": str(request.url.path),
        },
        media_type="application/problem+json",
    )


app.include_router(auth.router)
app.include_router(game.router)


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


if FRONTEND_DIR.exists():
    app.mount("/css", StaticFiles(directory=FRONTEND_DIR / "css"), name="css")
    app.mount("/js", StaticFiles(directory=FRONTEND_DIR / "js"), name="js")
    app.mount("/tests", StaticFiles(directory=FRONTEND_DIR / "tests"), name="tests")

    @app.get("/favicon.svg")
    async def serve_favicon() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "favicon.svg", media_type="image/svg+xml")

    @app.get("/")
    async def serve_frontend() -> FileResponse:
        return FileResponse(FRONTEND_DIR / "index.html")
