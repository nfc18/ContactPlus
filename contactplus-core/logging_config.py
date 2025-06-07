"""
Enhanced logging configuration for ContactPlus Core
"""
import os
import logging
import logging.handlers
from pathlib import Path


def setup_logging():
    """Configure comprehensive logging for the application"""
    
    # Create logs directory
    log_dir = Path("/app/logs")
    log_dir.mkdir(exist_ok=True)
    
    # Get log level from environment
    log_level = os.environ.get("LOG_LEVEL", "INFO").upper()
    
    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, log_level))
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler with detailed format
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    console_handler.setFormatter(console_formatter)
    root_logger.addHandler(console_handler)
    
    # File handler for application logs
    app_file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "contactplus.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    file_formatter = logging.Formatter(
        fmt="%(asctime)s [%(levelname)8s] %(name)s [%(filename)s:%(lineno)d] %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )
    app_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(app_file_handler)
    
    # Separate file for API access logs
    api_logger = logging.getLogger("uvicorn.access")
    api_file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "api_access.log",
        maxBytes=50 * 1024 * 1024,  # 50MB
        backupCount=10
    )
    api_file_handler.setFormatter(file_formatter)
    api_logger.addHandler(api_file_handler)
    
    # Error-only file handler
    error_file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "errors.log",
        maxBytes=10 * 1024 * 1024,  # 10MB
        backupCount=5
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(file_formatter)
    root_logger.addHandler(error_file_handler)
    
    # Database operations logger
    db_logger = logging.getLogger("contactplus.database")
    db_file_handler = logging.handlers.RotatingFileHandler(
        filename=log_dir / "database.log",
        maxBytes=20 * 1024 * 1024,  # 20MB
        backupCount=5
    )
    db_file_handler.setFormatter(file_formatter)
    db_logger.addHandler(db_file_handler)
    
    # Set specific logger levels
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.INFO)
    logging.getLogger("contactplus").setLevel(logging.DEBUG if log_level == "DEBUG" else logging.INFO)
    
    # Suppress noisy third-party loggers
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("requests").setLevel(logging.WARNING)
    
    return root_logger


class LoggerMixin:
    """Mixin to add logger to any class"""
    
    @property
    def logger(self):
        return logging.getLogger(f"contactplus.{self.__class__.__name__}")


def log_api_call(func):
    """Decorator to log API calls with timing"""
    import functools
    import time
    
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        logger = logging.getLogger("contactplus.api")
        start_time = time.time()
        
        try:
            result = await func(*args, **kwargs)
            duration = time.time() - start_time
            logger.info(f"{func.__name__} completed successfully in {duration:.3f}s")
            return result
        except Exception as e:
            duration = time.time() - start_time
            logger.error(f"{func.__name__} failed after {duration:.3f}s: {str(e)}")
            raise
    
    return wrapper