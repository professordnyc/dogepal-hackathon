"""
Logging configuration for the DOGEPAL application.

This module provides a centralized logging configuration that can be used across
the application. It sets up log formatting, file handlers, and log levels
based on the application's settings.
"""
import logging
import logging.config
import os
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from app.core.config import settings


def setup_logging() -> None:
    """
    Configure logging for the application.
    
    This function sets up logging with the following features:
    - Console logging with colored output in development
    - File logging in production
    - JSON formatting for structured logging
    - Log rotation based on size
    """
    log_level = logging.DEBUG if settings.DEBUG else logging.INFO
    log_dir = Path("logs")
    
    # Create logs directory if it doesn't exist
    log_dir.mkdir(exist_ok=True)
    
    # Base logging configuration
    logging_config: Dict[str, Any] = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "format": "%(asctime)s %(name)-12s %(levelname)-8s %(message)s",
                "class": "pythonjsonlogger.jsonlogger.JsonFormatter",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "json_ensure_ascii": False,
            },
            "colored": {
                "format": "%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
                "class": "logging.Formatter",
            },
            "simple": {
                "format": "%(asctime)s - %(name)-12s - %(levelname)-8s - %(message)s",
                "datefmt": "%Y-%m-%d %H:%M:%S",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": log_level,
                "formatter": "colored" if settings.DEBUG else "simple",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {  # root logger
                "handlers": ["console"],
                "level": log_level,
                "propagate": True,
            },
            "uvicorn": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "uvicorn.error": {
                "handlers": ["console"],
                "level": log_level,
                "propagate": False,
            },
            "sqlalchemy.engine": {
                "handlers": ["console"],
                "level": logging.WARNING if not settings.DEBUG else logging.INFO,
                "propagate": False,
            },
        },
    }
    
    # Add file handler in production
    if not settings.DEBUG:
        logging_config["handlers"]["file"] = {
            "class": "logging.handlers.RotatingFileHandler",
            "level": logging.INFO,
            "formatter": "json",
            "filename": log_dir / "app.log",
            "maxBytes": 10485760,  # 10MB
            "backupCount": 5,
            "encoding": "utf8",
        }
        logging_config["loggers"][""]["handlers"].append("file")
    
    # Apply the configuration
    logging.config.dictConfig(logging_config)
    
    # Set log level for specific loggers
    if settings.DEBUG:
        logging.getLogger("uvicorn").setLevel(log_level)
        logging.getLogger("uvicorn.access").disabled = True
        logging.getLogger("sqlalchemy.engine").setLevel(log_level)


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get a logger with the given name.
    
    Args:
        name: The name of the logger. If None, returns the root logger.
        
    Returns:
        A configured logger instance.
    """
    return logging.getLogger(name)


# Initialize logging when the module is imported
setup_logging()
