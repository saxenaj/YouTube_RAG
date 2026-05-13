"""
Logging Configuration Module

Provides centralized logging setup with:
- File and console output
- JSON formatting option
- Different log levels
- Rotation support
"""

import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = "youtube_rag",
    level: int = logging.INFO,
    log_file: Optional[str] = None,
    log_dir: str = "logs",
    max_bytes: int = 10 * 1024 * 1024,  # 10MB
    backup_count: int = 5,
    json_format: bool = False
) -> logging.Logger:
    """
    Setup and configure logger
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Log file name (optional, defaults to {name}_{date}.log)
        log_dir: Directory for log files
        max_bytes: Maximum log file size before rotation
        backup_count: Number of backup files to keep
        json_format: Use JSON formatting (useful for log aggregation)
    
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers to avoid duplicates
    logger.handlers.clear()
    
    # Create formatters
    if json_format:
        formatter = JsonFormatter()
    else:
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    # Console handler (stdout)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (with rotation)
    if log_file or log_dir:
        # Create log directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)
        
        # Generate log filename
        if not log_file:
            timestamp = datetime.now().strftime("%Y%m%d")
            log_file = f"{name}_{timestamp}.log"
        
        file_path = log_path / log_file
        
        file_handler = RotatingFileHandler(
            file_path,
            maxBytes=max_bytes,
            backupCount=backup_count
        )
        file_handler.setLevel(level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    Get or create a logger with the given name
    
    Args:
        name: Logger name (typically __name__ of the module)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class JsonFormatter(logging.Formatter):
    """
    Custom JSON formatter for structured logging
    """
    
    def format(self, record: logging.LogRecord) -> str:
        import json
        
        log_data = {
            'timestamp': datetime.fromtimestamp(record.created).isoformat(),
            'level': record.levelname,
            'logger': record.name,
            'module': record.module,
            'function': record.funcName,
            'line': record.lineno,
            'message': record.getMessage(),
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data['exception'] = self.formatException(record.exc_info)
        
        # Add extra fields if present
        if hasattr(record, 'extra'):
            log_data.update(record.extra)
        
        return json.dumps(log_data)


class LoggerMixin:
    """
    Mixin class to add logging capability to any class
    
    Usage:
        class MyService(LoggerMixin):
            def my_method(self):
                self.logger.info("Doing something")
    """
    
    @property
    def logger(self) -> logging.Logger:
        if not hasattr(self, '_logger'):
            self._logger = get_logger(self.__class__.__name__)
        return self._logger


# Convenience functions for different log levels
def debug(message: str, **kwargs):
    """Log debug message"""
    logger = get_logger(__name__)
    logger.debug(message, extra=kwargs)


def info(message: str, **kwargs):
    """Log info message"""
    logger = get_logger(__name__)
    logger.info(message, extra=kwargs)


def warning(message: str, **kwargs):
    """Log warning message"""
    logger = get_logger(__name__)
    logger.warning(message, extra=kwargs)


def error(message: str, exc_info: bool = False, **kwargs):
    """Log error message"""
    logger = get_logger(__name__)
    logger.error(message, exc_info=exc_info, extra=kwargs)


def critical(message: str, exc_info: bool = True, **kwargs):
    """Log critical message"""
    logger = get_logger(__name__)
    logger.critical(message, exc_info=exc_info, extra=kwargs)


# Initialize default logger
default_logger = setup_logger()