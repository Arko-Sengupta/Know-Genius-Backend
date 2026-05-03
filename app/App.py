from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address

from app.Api.Routes.Chat import Router as ChatRouter
RateLimiter = Limiter(key_func=get_remote_address, default_limits=["100/15minutes"])

def CreateApp() -> FastAPI:
    try:
        Application = FastAPI(
            title="Know-Genius API",
            description="Agentic general knowledge chatbot powered by Google Gemini",
            version="1.0.0",
            docs_url="/docs",
            redoc_url=None,
        )

        Application.state.limiter = RateLimiter
        Application.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

        Application.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_methods=["*"],
            allow_headers=["*"],
        )

        @Application.exception_handler(Exception)
        async def UnhandledExceptionHandler(_Request: Request, _Exc: Exception) -> JSONResponse:
            try:
                return JSONResponse(
                    status_code=500,
                    content={"error": "An unexpected error occurred. Please try again."},
                )
            except Exception as Error:
                raise Error

        Application.include_router(ChatRouter, prefix="/api")

        @Application.get("/health", tags=["health"])
        async def Health() -> dict:
            try:
                return {"status": "ok"}
            except Exception as Error:
                raise Error

        return Application
    except Exception as Error:
        raise Error