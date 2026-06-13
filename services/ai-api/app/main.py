from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.config import settings
from app.routers.invoices import router
from app.services.persistence import init_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title=settings.app_name,
    description=(
        "Tenant-aware document inference API. "
        "Supports PDF upload, async inference jobs, OpenAI structured extraction, "
        "deterministic validation, rule-based fallback, SQLite audit log, "
        "usage accounting, and in-memory latency/cost metrics."
    ),
    version=settings.app_version,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_origin_regex=settings.cors_allow_origin_regex,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(HTTPException)
async def http_exception_handler(_request: Request, exc: HTTPException):
    detail = exc.detail if isinstance(exc.detail, str) else "Request failed."
    return JSONResponse(
        status_code=exc.status_code,
        content={"error": detail, "detail": None},
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(_request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"error": "Request validation failed.", "detail": str(exc.errors())},
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(_request: Request, _exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"error": "Unexpected server error.", "detail": None},
    )


app.include_router(router, tags=["invoices"])
