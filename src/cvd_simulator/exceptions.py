"""Custom exceptions for the CVD Simulator application.

This module defines a hierarchy of exceptions used throughout the application
to provide meaningful error messages and enable proper error handling.
"""

from __future__ import annotations
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from pathlib import Path


class CVDSimulatorError(Exception):
    """Base exception for all CVD Simulator errors.

    All custom exceptions in this application inherit from this class,
    allowing users to catch all application-specific errors with a single
    except block.

    Example:
        >>> try:
        ...     simulator.process_image(path)
        ... except CVDSimulatorError as e:
        ...     print(f"Simulator error: {e}")
    """

    pass


class ImageProcessingError(CVDSimulatorError):
    """Exception raised when image loading or processing fails.

    This exception is raised in situations such as:
    - File not found
    - Invalid image format
    - Corrupted image data
    - Unsupported image mode
    - Memory errors during processing

    Attributes:
        path: Path to the image file that caused the error.
        original_error: The underlying exception that caused this error.

    Example:
        >>> try:
        ...     loader.load(Path("invalid.jpg"))
        ... except ImageProcessingError as e:
        ...     print(f"Failed to process {e.path}: {e}")
    """

    def __init__(
        self, message: str, path: Path | None = None, original_error: Exception | None = None
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            path: Path to the problematic image file.
            original_error: The original exception that caused this error.
        """
        super().__init__(message)
        self.path = path
        self.original_error = original_error


class SecurityError(CVDSimulatorError):
    """Exception raised when a security violation is detected.

    This exception is raised for security issues such as:
    - Path traversal attempts
    - Invalid file types
    - Files exceeding size limits
    - Suspicious file content

    Attributes:
        violation_type: Category of security violation.
        details: Additional information about the violation.

    Example:
        >>> try:
        ...     validator.validate_image(path)
        ... except SecurityError as e:
        ...     logger.warning(f"Security violation: {e.violation_type}")
    """

    def __init__(
        self, message: str, violation_type: str | None = None, details: dict[str, Any] | None = None
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            violation_type: Category of security violation.
            details: Additional context about the violation.
        """
        super().__init__(message)
        self.violation_type = violation_type
        self.details = details or {}


class ValidationError(CVDSimulatorError):
    """Exception raised when input validation fails.

    This exception is raised when:
    - Configuration values are invalid
    - Input parameters are out of range
    - Required parameters are missing
    - Data types don't match expectations

    Attributes:
        field: Name of the field that failed validation.
        value: The invalid value that was provided.
        constraint: Description of the validation constraint.

    Example:
        >>> try:
        ...     config = SimulationConfig(severity=1.5)  # Invalid: > 1.0
        ... except ValidationError as e:
        ...     print(f"Invalid {e.field}: {e.value} (must be {e.constraint})")
    """

    def __init__(
        self,
        message: str,
        field: str | None = None,
        value: Any = None,
        constraint: str | None = None,
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            field: Name of the validated field.
            value: The invalid value.
            constraint: Description of valid constraints.
        """
        super().__init__(message)
        self.field = field
        self.value = value
        self.constraint = constraint


class ConfigurationError(CVDSimulatorError):
    """Exception raised when configuration is invalid or missing.

    This exception is raised when:
    - Required configuration files are missing
    - Configuration values are incompatible
    - Environment variables are not set
    - Configuration cannot be parsed

    Attributes:
        config_key: The configuration key that caused the error.
        config_file: Path to the configuration file (if applicable).

    Example:
        >>> try:
        ...     config.load_from_file(path)
        ... except ConfigurationError as e:
        ...     print(f"Config error in {e.config_file}: {e}")
    """

    def __init__(
        self, message: str, config_key: str | None = None, config_file: Path | None = None
    ):
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            config_key: The problematic configuration key.
            config_file: Path to the configuration file.
        """
        super().__init__(message)
        self.config_key = config_key
        self.config_file = config_file


class BatchProcessingError(CVDSimulatorError):
    """Exception raised when batch processing fails.

    This exception is raised when:
    - Multiple files fail to process
    - Worker processes encounter errors
    - Batch configuration is invalid

    Attributes:
        failed_items: List of items that failed processing.
        success_count: Number of items successfully processed.

    Example:
        >>> try:
        ...     batch_processor.process_batch(files)
        ... except BatchProcessingError as e:
        ...     print(f"Failed: {len(e.failed_items)}, Succeeded: {e.success_count}")
    """

    def __init__(self, message: str, failed_items: list[Any] | None = None, success_count: int = 0):
        """Initialize the exception.

        Args:
            message: Human-readable error description.
            failed_items: List of items that failed.
            success_count: Number of successful items.
        """
        super().__init__(message)
        self.failed_items = failed_items or []
        self.success_count = success_count
