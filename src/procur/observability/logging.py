"""Structured logging with JSON format."""

import logging
import sys
from typing import Any, Dict, Optional

from pythonjsonlogger import jsonlogger


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    """Custom JSON formatter with additional context."""
    
    def add_fields(self, log_record: Dict[str, Any], record: logging.LogRecord, message_dict: Dict[str, Any]):
        """Add custom fields to log record."""
        super().add_fields(log_record, record, message_dict)
        
        # Add standard fields
        log_record['timestamp'] = self.formatTime(record, self.datefmt)
        log_record['level'] = record.levelname
        log_record['logger'] = record.name
        log_record['module'] = record.module
        log_record['function'] = record.funcName
        log_record['line'] = record.lineno
        
        # Add process/thread info
        log_record['process_id'] = record.process
        log_record['thread_id'] = record.thread
        
        # Add exception info if present
        if record.exc_info:
            log_record['exception'] = self.formatException(record.exc_info)
        
        # Add custom context if present
        if hasattr(record, 'user_id'):
            log_record['user_id'] = record.user_id
        if hasattr(record, 'organization_id'):
            log_record['organization_id'] = record.organization_id
        if hasattr(record, 'request_id'):
            log_record['request_id'] = record.request_id
        if hasattr(record, 'negotiation_id'):
            log_record['negotiation_id'] = record.negotiation_id
        if hasattr(record, 'correlation_id'):
            log_record['correlation_id'] = record.correlation_id


def setup_logging(
    level: str = "INFO",
    json_format: bool = True,
    log_file: Optional[str] = None,
) -> None:
    """
    Setup structured logging.
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        json_format: Use JSON format (True) or plain text (False)
        log_file: Optional log file path
    """
    # Create root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(getattr(logging, level.upper()))
    
    # Remove existing handlers
    root_logger.handlers = []
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level.upper()))
    
    if json_format:
        # JSON formatter
        formatter = CustomJsonFormatter(
            '%(timestamp)s %(level)s %(name)s %(message)s',
            datefmt='%Y-%m-%dT%H:%M:%S',
        )
    else:
        # Plain text formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S',
        )
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(getattr(logging, level.upper()))
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set levels for noisy libraries
    logging.getLogger('urllib3').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)
    logging.getLogger('openai').setLevel(logging.WARNING)
    
    logging.info("Structured logging initialized", extra={
        "level": level,
        "json_format": json_format,
        "log_file": log_file,
    })


def get_logger(name: str) -> logging.Logger:
    """
    Get logger with name.
    
    Args:
        name: Logger name (usually __name__)
    
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


class LogContext:
    """Context manager for adding context to logs."""
    
    def __init__(self, logger: logging.Logger, **context):
        """
        Initialize log context.
        
        Args:
            logger: Logger instance
            **context: Context fields (user_id, request_id, etc.)
        """
        self.logger = logger
        self.context = context
        self.old_factory = None
    
    def __enter__(self):
        """Enter context."""
        self.old_factory = logging.getLogRecordFactory()
        
        def record_factory(*args, **kwargs):
            record = self.old_factory(*args, **kwargs)
            for key, value in self.context.items():
                setattr(record, key, value)
            return record
        
        logging.setLogRecordFactory(record_factory)
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit context."""
        logging.setLogRecordFactory(self.old_factory)


def log_with_context(logger: logging.Logger, level: str, message: str, **context):
    """
    Log message with context.
    
    Args:
        logger: Logger instance
        level: Log level
        message: Log message
        **context: Additional context fields
    """
    with LogContext(logger, **context):
        getattr(logger, level.lower())(message)
