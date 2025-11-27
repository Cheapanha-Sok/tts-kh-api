import time
import logging
from src.logging_config import setup_logging
from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager

from src import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    server_error_handler,
    BaseAppException,
    synthesize_router,
    # create_db_tables
)
from src.setting import get_settings
from src.tts import TTS

settings = get_settings()
setup_logging()

# Lifespan context for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):

    # Create table if not exist
    start_time = time.time()
    # create_db_tables()
    # logger.info("Database tables created")

    # Load model and store it in state
    app.state.model = TTS(
        onnx_model_path=settings.model_path,
        execution_provider="CPUExecutionProvider",
        verbose=True
    )

    end_time = time.time()
    task_took_time = end_time - start_time
    logging.info(f"Background task took: {task_took_time:.2f}")
    
    yield
    # Clean up resources on shutdown
    del app.state.model
    logging.info("Application shutdown")
    
# Initialize FastAPI app with lifespan
app = FastAPI(
    docs_url=None,
    redoc_url=None,
    openapi_url=None,
    lifespan=lifespan
)

# Register custom exceptions
app.add_exception_handler(BaseAppException, app_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(Exception, server_error_handler)

# Register app router with prefix
app.include_router(router=synthesize_router, prefix="/api/v1")
