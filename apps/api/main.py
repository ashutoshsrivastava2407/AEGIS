"""AEGIS Platform API Application Entry Point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from packages.config import settings
from packages.observability import logger, get_correlation_id
from apps.api.middleware import CorrelationMiddleware
from apps.api.routers.v1 import api_v1_router, health_router
from apps.api.schemas import ErrorResponse, ErrorDetail

app = FastAPI(
    title="AEGIS Enterprise Intelligence Platform API",
    description="Autonomous Enterprise Intelligence & Decision Operating System API",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# Middleware Stack
app.add_middleware(CorrelationMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.API_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    correlation_id = get_correlation_id()
    logger.error(f"Unhandled Exception on {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            status_code=500,
            error=ErrorDetail(
                code="INTERNAL_SERVER_ERROR",
                message="An unexpected server error occurred",
                details=str(exc) if settings.AEGIS_ENV == "development" else None,
            ),
            correlation_id=correlation_id,
        ).model_dump(),
    )


# Health routers mounted at root level
app.include_router(health_router)

# Versioned API routes mounted at /api/v1
app.include_router(api_v1_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "apps.api.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.AEGIS_ENV == "development",
    )
