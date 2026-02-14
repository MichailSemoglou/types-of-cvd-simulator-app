"""Unit tests for security validators."""

from __future__ import annotations
from pathlib import Path

import pytest
from PIL import Image

from cvd_simulator.exceptions import SecurityError, ValidationError
from cvd_simulator.utils.validators import SecurityValidator


class TestSecurityValidator:
    """Tests for SecurityValidator class."""

    def test_initialization_default(self):
        """Test validator initialization with defaults."""
        validator = SecurityValidator()

        assert validator.max_file_size == 100 * 1024 * 1024  # 100MB
        assert validator.max_dimension == 10000
        assert validator.allowed_formats == SecurityValidator.ALLOWED_FORMATS

    def test_initialization_custom(self):
        """Test validator initialization with custom values."""
        validator = SecurityValidator(
            max_file_size=1024 * 1024, max_dimension=5000, allowed_formats={"png", "jpg"}  # 1MB
        )

        assert validator.max_file_size == 1024 * 1024
        assert validator.max_dimension == 5000
        assert validator.allowed_formats == {"png", "jpg"}

    def test_initialization_invalid_max_file_size(self):
        """Test that negative max_file_size raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SecurityValidator(max_file_size=-1)

        assert exc_info.value.field == "max_file_size"

    def test_initialization_invalid_max_dimension(self):
        """Test that negative max_dimension raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SecurityValidator(max_dimension=-1)

        assert exc_info.value.field == "max_dimension"

    def test_validate_image_not_found(self, validator: SecurityValidator):
        """Test validation of non-existent file."""
        with pytest.raises(SecurityError) as exc_info:
            validator.validate_image(Path("/nonexistent/file.png"))

        assert exc_info.value.violation_type == "FILE_NOT_FOUND"

    def test_validate_image_directory(self, validator: SecurityValidator, tmp_path: Path):
        """Test validation of directory instead of file."""
        with pytest.raises(SecurityError) as exc_info:
            validator.validate_image(tmp_path)

        assert exc_info.value.violation_type == "NOT_A_FILE"

    def test_validate_image_empty_file(self, validator: SecurityValidator, tmp_path: Path):
        """Test validation of empty file."""
        empty_file = tmp_path / "empty.png"
        empty_file.touch()

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_image(empty_file)

        assert exc_info.value.violation_type == "EMPTY_FILE"

    def test_validate_image_too_large(self, tmp_path: Path):
        """Test validation of file exceeding size limit."""
        validator = SecurityValidator(max_file_size=100)  # 100 bytes

        # Create a larger file
        large_file = tmp_path / "large.png"
        img = Image.new("RGB", (100, 100), color="red")
        img.save(large_file)

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_image(large_file)

        assert exc_info.value.violation_type == "FILE_TOO_LARGE"

    def test_validate_image_invalid_format(self, validator: SecurityValidator, tmp_path: Path):
        """Test validation of file with invalid format."""
        invalid_file = tmp_path / "test.txt"
        invalid_file.write_text("not an image")

        with pytest.raises(SecurityError) as exc_info:
            validator.validate_image(invalid_file)

        assert exc_info.value.violation_type == "UNKNOWN_FORMAT"

    def test_validate_image_valid(self, validator: SecurityValidator, sample_image_path: Path):
        """Test validation of valid image file."""
        # Should not raise any exception
        validator.validate_image(sample_image_path)

    def test_sanitize_filename_path_traversal(self, validator: SecurityValidator):
        """Test sanitization of path traversal attempts."""
        result = validator.sanitize_filename("../../../etc/passwd")

        assert ".." not in result
        assert "/" not in result

    def test_sanitize_filename_special_chars(self, validator: SecurityValidator):
        """Test sanitization of special characters."""
        result = validator.sanitize_filename("my file:name?.jpg")

        assert ":" not in result
        assert "?" not in result
        assert " " not in result

    def test_sanitize_filename_empty(self, validator: SecurityValidator):
        """Test sanitization of empty filename."""
        result = validator.sanitize_filename("")

        assert result == "unnamed_file"

    def test_sanitize_output_path_valid(self, validator: SecurityValidator, tmp_path: Path):
        """Test sanitization of valid output path."""
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        result = validator.sanitize_output_path(output_dir, "image.jpg")

        assert result.parent == output_dir
        assert result.name == "image.jpg"

    def test_sanitize_output_path_traversal(self, validator: SecurityValidator, tmp_path: Path):
        """Test sanitization of output path with traversal attempt."""
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        # Path traversal in filename is sanitized to safe name
        result = validator.sanitize_output_path(output_dir, "../../../etc/passwd")

        # Should be sanitized and within output directory
        assert result.parent == output_dir
        assert ".." not in result.name
        assert "/" not in result.name
        assert "etc_passwd" in result.name
        assert result.name.startswith("_")
