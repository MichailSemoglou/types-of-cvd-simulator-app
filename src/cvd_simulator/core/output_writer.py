"""Output writing module for the CVD Simulator application.

This module provides functionality for saving processed images
with proper optimization and error handling.
"""

from __future__ import annotations
from datetime import datetime
from pathlib import Path
from typing import Any

from PIL import Image

from cvd_simulator.config import SimulationConfig
from cvd_simulator.enums import CVDType, OutputFormat
from cvd_simulator.exceptions import ImageProcessingError
from cvd_simulator.utils.logging_config import get_logger
from cvd_simulator.utils.validators import SecurityValidator

logger = get_logger(__name__)


class OutputWriter:
    """Writes processed images to disk with optimization.

    This class handles saving images with proper format-specific
    optimization settings and generates organized output filenames.

    Attributes:
        config: SimulationConfig with output settings.
        validator: SecurityValidator for path sanitization.

    Example:
        >>> writer = OutputWriter(config)
        >>> path = writer.save(image, CVDType.PROTAN, timestamp)
    """

    def __init__(
        self, config: SimulationConfig | None = None, validator: SecurityValidator | None = None
    ):
        """Initialize the output writer.

        Args:
            config: Optional SimulationConfig. Uses defaults if not provided.
            validator: Optional SecurityValidator for path validation.
        """
        self.config = config or SimulationConfig()
        self.validator = validator or SecurityValidator()
        logger.debug(f"OutputWriter initialized with format: {self.config.output_format}")

    def save(
        self,
        image: Image.Image,
        cvd_type: CVDType,
        timestamp: str | None = None,
        custom_name: str | None = None,
    ) -> Path:
        """Save an image with appropriate settings.

        Generates an output filename based on the CVD type and timestamp,
        ensures the output directory exists, and saves with format-specific
        optimization settings.

        Args:
            image: PIL Image to save.
            cvd_type: Type of CVD simulation (for filename generation).
            timestamp: Optional timestamp string. Uses current time if not provided.
            custom_name: Optional custom filename base (instead of cvd_type).

        Returns:
            Path to the saved file.

        Raises:
            ImageProcessingError: If saving fails.

        Example:
            >>> writer = OutputWriter(config)
            >>> path = writer.save(image, CVDType.PROTAN)
            >>> print(path)
            outputs/protan_image_20260212_153045.jpg
        """
        # Generate timestamp if not provided
        if timestamp is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

        # Generate output path
        output_path = self._generate_output_path(cvd_type, timestamp, custom_name)

        # Ensure output directory exists
        self.config.output_directory.mkdir(parents=True, exist_ok=True)

        logger.info(f"Saving image: {output_path}")

        try:
            # Get format-specific settings
            settings = self._get_format_settings()

            # Save the image
            image.save(output_path, **settings)

            logger.info(f"Image saved successfully: {output_path}")
            return output_path

        except Exception as e:
            logger.error(f"Failed to save image: {e}")
            raise ImageProcessingError(
                f"Failed to save image to {output_path}: {e}", original_error=e
            )

    def _generate_output_path(
        self, cvd_type: CVDType, timestamp: str, custom_name: str | None = None
    ) -> Path:
        """Generate the output file path.

        Args:
            cvd_type: Type of CVD simulation.
            timestamp: Timestamp string for the filename.
            custom_name: Optional custom filename base.

        Returns:
            Path object for the output file.
        """
        name_base = custom_name or f"{cvd_type.value}_image"
        filename = f"{name_base}_{timestamp}.{self.config.output_format.value}"

        # Sanitize and create full path
        return self.validator.sanitize_output_path(self.config.output_directory, filename)

    def _get_format_settings(self) -> dict[str, Any]:
        """Get format-specific save settings.

        Returns:
            Dictionary of keyword arguments for PIL Image.save().
        """
        fmt = self.config.output_format

        settings = {
            "format": fmt.pil_format,
        }

        if fmt == OutputFormat.JPEG:
            settings.update(
                {
                    "quality": self.config.quality,
                    "optimize": self.config.optimize,
                }
            )
        elif fmt == OutputFormat.PNG:
            settings.update(
                {
                    "optimize": self.config.optimize,
                }
            )
        elif fmt == OutputFormat.WEBP:
            settings.update(
                {
                    "quality": self.config.quality,
                    "method": 6,  # Best compression
                }
            )

        return settings

    def optimize_save(
        self, image: Image.Image, output_path: Path, quality: int | None = None
    ) -> Path:
        """Save an image with explicit optimization settings.

        This is a more explicit version of save() for when you need
        fine-grained control over optimization parameters.

        Args:
            image: PIL Image to save.
            output_path: Path where the image should be saved.
            quality: Optional quality override (1-95).

        Returns:
            Path to the saved file.

        Raises:
            ImageProcessingError: If saving fails.
        """
        # Ensure directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Sanitize the path
        safe_path = self.validator.sanitize_output_path(output_path.parent, output_path.name)

        logger.info(f"Optimizing and saving: {safe_path}")

        try:
            # Determine format from extension
            ext = safe_path.suffix.lower()
            format_mapping = {
                ".jpg": "JPEG",
                ".jpeg": "JPEG",
                ".png": "PNG",
                ".webp": "WEBP",
                ".tiff": "TIFF",
                ".tif": "TIFF",
                ".bmp": "BMP",
            }

            pil_format = format_mapping.get(ext, "JPEG")

            # Build settings
            settings = {"format": pil_format}

            if pil_format == "JPEG":
                settings.update(
                    {
                        "quality": quality or self.config.quality,
                        "optimize": True,
                    }
                )
            elif pil_format == "PNG":
                settings.update(
                    {
                        "optimize": True,
                    }
                )
            elif pil_format == "WEBP":
                settings.update(
                    {
                        "quality": quality or self.config.quality,
                        "method": 6,
                    }
                )

            image.save(safe_path, **settings)

            logger.info(f"Image optimized and saved: {safe_path}")
            return safe_path

        except Exception as e:
            logger.error(f"Failed to optimize save: {e}")
            raise ImageProcessingError(f"Failed to save optimized image: {e}", original_error=e)
