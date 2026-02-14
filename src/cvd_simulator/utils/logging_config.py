"""Logging configuration for the CVD Simulator application.

This module provides centralized logging setup with support for
console and file output, formatting, and log level configuration.
"""

from __future__ import annotations
import logging
import sys
from pathlib import Path

from cvd_simulator.enums import LogLevel


class ColoredFormatter(logging.Formatter):
    """Custom formatter that adds color to console output.
    
    This formatter uses ANSI escape codes to colorize log messages
    based on their severity level, making them easier to read.
    
    Attributes:
        COLORS: Mapping of log levels to ANSI color codes.
    """
    
    # ANSI color codes
    COLORS = {
        "DEBUG": "\033[36m",      # Cyan
        "INFO": "\033[32m",       # Green
        "WARNING": "\033[33m",    # Yellow
        "ERROR": "\033[31m",      # Red
        "CRITICAL": "\033[35m",   # Magenta
        "RESET": "\033[0m",       # Reset
    }
    
    def format(self, record: logging.LogRecord) -> str:
        """Format a log record with color.
        
        Args:
            record: The log record to format.
        
        Returns:
            Formatted and colorized log message.
        """
        # Get color for this level
        color = self.COLORS.get(record.levelname, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        
        # Add color to levelname
        original_levelname = record.levelname
        record.levelname = f"{color}{original_levelname}{reset}"
        
        # Format the message
        result = super().format(record)
        
        # Restore original levelname
        record.levelname = original_levelname
        
        return result


def setup_logging(
    level: LogLevel = LogLevel.INFO,
    log_file: Path | None = None,
    log_format: str | None = None,
    use_colors: bool = True,
) -> logging.Logger:
    """Set up logging for the application.
    
    Configures the root logger with console output and optional
    file output. Uses colored output for the console if requested.
    
    Args:
        level: Minimum log level to display.
        log_file: Optional path to log file for file output.
        log_format: Custom format string for log messages.
        use_colors: Whether to use colored output for console.
    
    Returns:
        Configured root logger instance.
    
    Example:
        >>> from cvd_simulator.utils.logging_config import setup_logging
        >>> logger = setup_logging(level=LogLevel.DEBUG, log_file=Path("app.log"))
        >>> logger.info("Application started")
    
    Notes:
        - Clears any existing handlers before setting up new ones.
        - File output always uses plain text (no colors).
        - Creates log file directory if it doesn't exist.
    """
    # Default format
    if log_format is None:
        log_format = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
    
    # Get the root logger for this package
    logger = logging.getLogger("cvd_simulator")
    logger.setLevel(level.value)
    
    # Clear existing handlers
    logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(level.value)
    
    if use_colors and sys.stdout.isatty():
        console_formatter = ColoredFormatter(log_format)
    else:
        console_formatter = logging.Formatter(log_format)
    
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # File handler (if requested)
    if log_file:
        # Create directory if needed
        log_file.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level.value)
        file_formatter = logging.Formatter(log_format)
        file_handler.setFormatter(file_formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """Get a logger with the specified name.
    
    This is a convenience function that returns a logger child
    of the cvd_simulator package logger.
    
    Args:
        name: Name for the logger, typically __name__.
    
    Returns:
        Logger instance with the specified name.
    
    Example:
        >>> from cvd_simulator.utils.logging_config import get_logger
        >>> logger = get_logger(__name__)
        >>> logger.info("Processing image...")
    """
    return logging.getLogger(f"cvd_simulator.{name}")