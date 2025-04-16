"""
Logging utilities for People Analytics.

This module provides functions for setting up and configuring logging
throughout the application.
"""

import logging
import os
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional, Union

# Default log format
DEFAULT_LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
DEFAULT_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

# Default log levels
LOG_LEVELS = {
    "debug": logging.DEBUG,
    "info": logging.INFO,
    "warning": logging.WARNING,
    "error": logging.ERROR,
    "critical": logging.CRITICAL,
}


def get_module_logger(module_name: str) -> logging.Logger:
    """
    Get a logger for a specific module.

    Args:
        module_name: The name of the module (usually __name__)

    Returns:
        logging.Logger: Configured logger for the module
    """
    return logging.getLogger(module_name)


def configure_root_logger(
    level: Union[str, int] = "info",
    log_file: Optional[Union[str, Path]] = None,
    log_format: str = DEFAULT_LOG_FORMAT,
    date_format: str = DEFAULT_DATE_FORMAT,
    console_output: bool = True,
) -> logging.Logger:
    """
    Configure the root logger for the application.

    Args:
        level: Log level (debug, info, warning, error, critical) or integer level
        log_file: Path to log file (if None, no file logging)
        log_format: Format string for log messages
        date_format: Format string for dates in log messages
        console_output: Whether to output logs to console

    Returns:
        logging.Logger: Configured root logger
    """
    # Get the root logger
    root_logger = logging.getLogger()

    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)

    # Determine log level
    if isinstance(level, str):
        log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    else:
        log_level = level

    # Set log level
    root_logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(log_format, date_format)

    # Add console handler if requested
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        root_logger.addHandler(console_handler)

    # Add file handler if log_file provided
    if log_file:
        log_path = Path(log_file)

        # Create directory if it doesn't exist
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(log_path, encoding="utf-8")
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)

    return root_logger


def create_run_logger(
    base_log_dir: Union[str, Path] = "logs",
    app_name: str = "peopleanalytics",
    level: Union[str, int] = "info",
    console_output: bool = True,
) -> logging.Logger:
    """
    Create a logger for a specific run with timestamped log file.

    Args:
        base_log_dir: Base directory for logs
        app_name: Application name (used in the log file name)
        level: Log level
        console_output: Whether to output logs to console

    Returns:
        logging.Logger: Configured logger for the run
    """
    # Create timestamp for the run
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Create log directory with app name
    log_dir = Path(base_log_dir) / app_name
    log_dir.mkdir(parents=True, exist_ok=True)

    # Create log file path
    log_file = log_dir / f"{app_name}_{timestamp}.log"

    # Configure root logger
    logger = configure_root_logger(
        level=level,
        log_file=log_file,
        console_output=console_output,
    )

    # Log start of run
    logger.info(f"Starting {app_name} run at {timestamp}")
    logger.info(f"Log file: {log_file}")

    return logger


def log_environment_info(logger: logging.Logger) -> None:
    """
    Log information about the execution environment.

    Args:
        logger: Logger to use
    """
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Platform: {sys.platform}")
    logger.info(f"Current working directory: {os.getcwd()}")

    # Log environment variables (excluding sensitive ones)
    exclude_vars = {"PASSWORD", "SECRET", "TOKEN", "KEY", "AUTH"}
    env_vars = {
        k: v
        for k, v in os.environ.items()
        if not any(exclude in k.upper() for exclude in exclude_vars)
    }

    logger.debug(f"Environment variables: {env_vars}")


def log_execution_params(logger: logging.Logger, params: Dict) -> None:
    """
    Log execution parameters.

    Args:
        logger: Logger to use
        params: Dictionary of parameters to log
    """
    logger.info("Execution parameters:")
    for key, value in params.items():
        logger.info(f"  {key}: {value}")


def setup_logger(
    module_name: str,
    level: Union[str, int] = "info",
    log_file: Optional[Union[str, Path]] = None,
) -> logging.Logger:
    """
    Setup a logger for a module with custom configuration.

    Args:
        module_name: Module name
        level: Log level
        log_file: Log file path (optional)

    Returns:
        logging.Logger: Configured logger
    """
    logger = logging.getLogger(module_name)

    # Determine log level
    if isinstance(level, str):
        log_level = LOG_LEVELS.get(level.lower(), logging.INFO)
    else:
        log_level = level

    logger.setLevel(log_level)

    # Create formatter
    formatter = logging.Formatter(DEFAULT_LOG_FORMAT, DEFAULT_DATE_FORMAT)

    # Add handlers if there are none
    if not logger.handlers:
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # File handler if provided
        if log_file:
            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(log_path, encoding="utf-8")
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

    return logger
