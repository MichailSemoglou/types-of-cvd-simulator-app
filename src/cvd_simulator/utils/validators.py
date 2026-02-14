"""Security validators for the CVD Simulator application.

This module provides validation functions to ensure input files
are safe to process, preventing security issues like path traversal
and malicious file uploads.
"""

from __future__ import annotations
from pathlib import Path

from PIL import Image

from cvd_simulator.exceptions import SecurityError, ValidationError


def _get_image_format(file_path: Path) -> str | None:
    """Detect image format using PIL.
    
    Args:
        file_path: Path to the image file.
    
    Returns:
        Image format string (lowercase) or None if unknown.
    """
    try:
        with Image.open(file_path) as img:
            fmt = img.format
            return fmt.lower() if fmt else None
    except Exception:
        return None


class SecurityValidator:
    """Security validation for input files and paths.
    
    This class provides methods to validate that input files are safe
    to process, checking for issues like path traversal, invalid formats,
    and suspicious file content.
    
    Attributes:
        allowed_formats: Set of allowed image format strings.
        max_file_size: Maximum allowed file size in bytes.
        max_dimension: Maximum allowed image dimension in pixels.
    
    Example:
        >>> validator = SecurityValidator(
        ...     max_file_size=10*1024*1024,  # 10MB
        ...     max_dimension=5000
        ... )
        >>> validator.validate_image(Path("photo.jpg"))
    """
    
    # Allowed image formats (PIL format names, lowercase)
    ALLOWED_FORMATS = {"jpeg", "png", "gif", "bmp", "tiff", "webp"}
    
    def __init__(
        self,
        max_file_size: int = 100 * 1024 * 1024,  # 100MB
        max_dimension: int = 10000,
        allowed_formats: set[str] | None = None,
    ):
        """Initialize the security validator.
        
        Args:
            max_file_size: Maximum allowed file size in bytes.
            max_dimension: Maximum allowed image dimension in pixels.
            allowed_formats: Set of allowed image format strings.
        
        Raises:
            ValidationError: If any parameter is invalid.
        """
        if max_file_size < 1:
            raise ValidationError(
                f"max_file_size must be positive, got {max_file_size}",
                field="max_file_size",
                value=max_file_size,
                constraint="max_file_size > 0"
            )
        
        if max_dimension < 1:
            raise ValidationError(
                f"max_dimension must be positive, got {max_dimension}",
                field="max_dimension",
                value=max_dimension,
                constraint="max_dimension > 0"
            )
        
        self.max_file_size = max_file_size
        self.max_dimension = max_dimension
        self.allowed_formats = allowed_formats or self.ALLOWED_FORMATS
    
    def validate_image(self, file_path: Path | str) -> None:
        """Validate an image file for security.
        
        Performs comprehensive validation including:
        - File existence and readability
        - File size limits
        - Image format validation
        - Image dimension limits
        - Basic corruption checks
        
        Args:
            file_path: Path to the image file to validate.
        
        Raises:
            SecurityError: If file fails any security check.
        
        Example:
            >>> validator = SecurityValidator()
            >>> validator.validate_image(Path("image.png"))
            # Raises SecurityError if invalid
        """
        # Convert to Path if string
        if isinstance(file_path, str):
            file_path = Path(file_path)
        
        # Check file exists
        if not file_path.exists():
            raise SecurityError(
                f"File not found: {file_path}",
                violation_type="FILE_NOT_FOUND",
                details={"path": str(file_path)}
            )
        
        # Check it's a file (not a directory)
        if not file_path.is_file():
            raise SecurityError(
                f"Path is not a file: {file_path}",
                violation_type="NOT_A_FILE",
                details={"path": str(file_path)}
            )
        
        # Check file size
        file_size = file_path.stat().st_size
        if file_size > self.max_file_size:
            raise SecurityError(
                f"File too large: {file_size} bytes (max: {self.max_file_size})",
                violation_type="FILE_TOO_LARGE",
                details={
                    "path": str(file_path),
                    "size": file_size,
                    "max_size": self.max_file_size
                }
            )
        
        # Check file is not empty
        if file_size == 0:
            raise SecurityError(
                f"File is empty: {file_path}",
                violation_type="EMPTY_FILE",
                details={"path": str(file_path)}
            )
        
        # Validate image format
        image_type = _get_image_format(file_path)
        if image_type is None:
            raise SecurityError(
                f"Cannot determine image type: {file_path}",
                violation_type="UNKNOWN_FORMAT",
                details={"path": str(file_path)}
            )
        
        if image_type not in self.allowed_formats:
            raise SecurityError(
                f"Image format not allowed: {image_type}",
                violation_type="DISALLOWED_FORMAT",
                details={
                    "path": str(file_path),
                    "format": image_type,
                    "allowed_formats": list(self.allowed_formats)
                }
            )
        
        # Open with PIL to check dimensions and corruption
        try:
            with Image.open(file_path) as img:
                # Verify the image (checks for corruption)
                img.verify()
                
                # Need to reopen after verify
                with Image.open(file_path) as img2:
                    width, height = img2.size
                    
                    if width > self.max_dimension or height > self.max_dimension:
                        raise SecurityError(
                            f"Image dimensions too large: {width}x{height} "
                            f"(max: {self.max_dimension}x{self.max_dimension})",
                            violation_type="DIMENSIONS_TOO_LARGE",
                            details={
                                "path": str(file_path),
                                "width": width,
                                "height": height,
                                "max_dimension": self.max_dimension
                            }
                        )
                    
        except SecurityError:
            raise
        except Exception as e:
            raise SecurityError(
                f"Invalid or corrupted image file: {e}",
                violation_type="CORRUPTED_FILE",
                details={"path": str(file_path), "error": str(e)}
            )
    
    def sanitize_filename(self, filename: str) -> str:
        """Sanitize a filename to prevent security issues.
        
        Removes or replaces dangerous characters and ensures the
        filename doesn't contain path traversal attempts.
        
        Args:
            filename: The original filename.
        
        Returns:
            Sanitized filename safe for use.
        
        Example:
            >>> validator = SecurityValidator()
            >>> validator.sanitize_filename("../../../etc/passwd")
            'etc_passwd'
            >>> validator.sanitize_filename("my file:name?.jpg")
            'my_file_name_.jpg'
        """
        # Remove path separators and null bytes
        dangerous = ['/', '\\', '\x00', '..']
        result = filename
        
        for char in dangerous:
            result = result.replace(char, '_')
        
        # Remove other dangerous characters
        safe_chars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-')
        result = ''.join(c if c in safe_chars else '_' for c in result)
        
        # Ensure not empty
        if not result or result == '_':
            result = 'unnamed_file'
        
        return result
    
    def sanitize_output_path(
        self, 
        output_dir: Path, 
        filename: str
    ) -> Path:
        """Sanitize output path to prevent directory traversal.
        
        Ensures the resolved output path is within the specified
        output directory, preventing path traversal attacks.
        
        Args:
            output_dir: Base output directory.
            filename: Desired filename.
        
        Returns:
            Safe output path within output_dir.
        
        Raises:
            SecurityError: If path traversal is detected.
        
        Example:
            >>> validator = SecurityValidator()
            >>> path = validator.sanitize_output_path(
            ...     Path("/safe/output"),
            ...     "image.jpg"
            ... )
            >>> print(path)
            /safe/output/image.jpg
        """
        # Normalize and resolve paths
        output_dir = output_dir.resolve()
        
        # Sanitize filename
        safe_filename = self.sanitize_filename(filename)
        
        # Create target path
        target = (output_dir / safe_filename).resolve()
        
        # Ensure target is within output directory
        try:
            target.relative_to(output_dir)
        except ValueError:
            raise SecurityError(
                f"Path traversal detected: {filename}",
                violation_type="PATH_TRAVERSAL",
                details={
                    "output_dir": str(output_dir),
                    "filename": filename,
                    "resolved": str(target)
                }
            )
        
        return target