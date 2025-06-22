"""
Logging configuration for the AI Task Manager.

This module sets up logging with a consistent format and log levels.
"""
import os
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Create logs directory if it doesn't exist
LOG_DIR = Path(__file__).parent / "logs"
LOG_DIR.mkdir(exist_ok=True)

# Log file paths
LOG_FILE = LOG_DIR / "task_manager.log"
ERROR_LOG_FILE = LOG_DIR / "task_manager_errors.log"

# Log format
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Maximum log file size (10MB)
MAX_LOG_SIZE = 10 * 1024 * 1024
# Number of backup logs to keep
BACKUP_COUNT = 5

def setup_logger(name: str = None, log_level: int = logging.INFO) -> logging.Logger:
    """
    Set up a logger with the specified name and log level.
    
    Args:
        name: The name of the logger. If None, returns the root logger.
        log_level: The log level (e.g., logging.INFO, logging.DEBUG).
        
    Returns:
        The configured logger instance.
    """
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Don't add handlers if they're already set up
    if logger.handlers:
        return logger
    
    # Create formatter
    formatter = logging.Formatter(LOG_FORMAT, LOG_DATE_FORMAT)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler for all logs
    file_handler = RotatingFileHandler(
        LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Error file handler (only ERROR level and above)
    error_file_handler = RotatingFileHandler(
        ERROR_LOG_FILE,
        maxBytes=MAX_LOG_SIZE,
        backupCount=BACKUP_COUNT,
        encoding='utf-8'
    )
    error_file_handler.setLevel(logging.ERROR)
    error_file_handler.setFormatter(formatter)
    logger.addHandler(error_file_handler)
    
    return logger

# Set up root logger
root_logger = setup_logger()

# Example usage:
# from logging_config import setup_logger
# logger = setup_logger(__name__)
