"""
Logging configuration for MCP Client
"""
import logging
import sys
from typing import Optional

# Default logger name
DEFAULT_LOGGER_NAME = "mcp"

# Create a default logger
_logger: Optional[logging.Logger] = None


def get_logger(name: Optional[str] = None) -> logging.Logger:
    """
    Get or create a logger instance.
    
    Args:
        name: Logger name. If None, uses the default MCP logger.
    
    Returns:
        logging.Logger: Configured logger instance
    """
    global _logger
    
    if name is None:
        if _logger is None:
            _logger = _setup_default_logger()
        return _logger
    
    # Ensure the root MCP logger is set up first
    if _logger is None:
        _logger = _setup_default_logger()
    
    # Get or create a child logger
    logger = logging.getLogger(name)
    
    # If this logger has no handlers, add one
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
        logger.setLevel(logging.INFO)
    
    return logger


def _setup_default_logger() -> logging.Logger:
    """
    Setup the default MCP logger with console handler.
    
    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(DEFAULT_LOGGER_NAME)
    
    # Only add handler if none exists
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter(
            fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    
    # Set default level to INFO
    logger.setLevel(logging.INFO)
    
    return logger


def set_log_level(level: str) -> None:
    """
    Set the logging level for the default MCP logger.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    """
    logger = get_logger()
    logger.setLevel(getattr(logging, level.upper()))


def configure_logging(
    level: str = "INFO",
    format_string: Optional[str] = None,
    date_format: Optional[str] = None
) -> None:
    """
    Configure the MCP logging system.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        format_string: Custom format string for log messages
        date_format: Custom date format string
    """
    logger = get_logger()
    logger.setLevel(getattr(logging, level.upper()))
    
    if format_string or date_format:
        # Remove existing handlers
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Add new handler with custom format
        handler = logging.StreamHandler(sys.stderr)
        formatter = logging.Formatter(
            fmt=format_string or '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt=date_format or '%Y-%m-%d %H:%M:%S'
        )
        handler.setFormatter(formatter)
        logger.addHandler(handler)
