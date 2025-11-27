from src.apis.synthesize import synthesize_router
from src.exceptions.handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    server_error_handler,
)
from src.exceptions.custom_exceptions import BaseAppException
# from src.db.config import create_db_tables