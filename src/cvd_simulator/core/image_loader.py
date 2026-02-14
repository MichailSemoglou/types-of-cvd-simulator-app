"""Image loading module for the CVD Simulator application.

This module provides functionality for loading and validating images
with proper error handling and security checks.
"""

from __future__ import annotations
from pathlib import Path
from typing import Any

import numpy as np
from PIL import Image

from cvd_simulator.exceptions import ImageProcessingError
from cvd_simulator.utils.logging_config import get_logger
from cvd_simulator.utils.validators import SecurityValidator

logger = get_logger(__name__)


class ImageLoader:
    """Loads and validates images for CVD simulation.

    This class handles image loading with proper validation,
    format conversion, and error handling. It ensures that images
    are safe to process and in the correct format for simulation.

    Attributes:
        validator: SecurityValidator instance for input validation.

    Example:
        >>> loader = ImageLoader()
        >>> image = loader.load(Path("photo.jpg"))
        >>> arr = loader.to_numpy(image)
    """

    def __init__(self, validator: SecurityValidator | None = None):
        """Initialize the image loader.

        Args:
            validator: Optional SecurityValidator for input validation.
                If not provided, a default validator is used.
        """
        self.validator = validator or SecurityValidator()
        logger.debug("ImageLoader initialized")

    def load(self, image_path: Path | str) -> Image.Image:
        """Load and validate an image file.

        Loads the image from the specified path, validates it for
        security, and converts it to RGB format if necessary.

        Args:
            image_path: Path to the image file.

        Returns:
            Loaded PIL Image in RGB mode.

        Raises:
            ImageProcessingError: If loading or validation fails.

        Example:
            >>> loader = ImageLoader()
            >>> image = loader.load(Path("input.png"))
            >>> print(image.mode)
            'RGB'
        """
        # Convert to Path
        if isinstance(image_path, str):
            image_path = Path(image_path)

        logger.info(f"Loading image: {image_path}")

        try:
            # Validate the file
            self.validator.validate_image(image_path)
            logger.debug(f"Image validation passed: {image_path}")

            # Open the image
            image = Image.open(image_path)
            logger.debug(f"Image opened: {image.format} {image.mode} {image.size}")

            # Convert to RGB if necessary
            if image.mode != "RGB":
                logger.debug(f"Converting from {image.mode} to RGB")
                image = image.convert("RGB")

            logger.info(f"Image loaded successfully: {image.size}")
            return image

        except ImageProcessingError:
            raise
        except Exception as e:
            logger.error(f"Failed to load image {image_path}: {e}")
            raise ImageProcessingError(
                f"Failed to load image: {e}", path=image_path, original_error=e
            )

    def to_numpy(self, image: Image.Image) -> np.ndarray:
        """Convert a PIL Image to a numpy array.

        Args:
            image: PIL Image to convert.

        Returns:
            Numpy array with shape (H, W, 3) and dtype uint8.

        Raises:
            ImageProcessingError: If conversion fails.

        Example:
            >>> loader = ImageLoader()
            >>> image = loader.load(Path("input.jpg"))
            >>> arr = loader.to_numpy(image)
            >>> print(arr.shape)
            (1080, 1920, 3)
        """
        try:
            arr = np.asarray(image)
            logger.debug(f"Converted image to numpy array: {arr.shape}")
            return arr
        except Exception as e:
            logger.error(f"Failed to convert image to numpy: {e}")
            raise ImageProcessingError(
                f"Failed to convert image to numpy array: {e}", original_error=e
            )

    def from_numpy(self, array: np.ndarray) -> Image.Image:
        """Convert a numpy array to a PIL Image.

        Args:
            array: Numpy array with shape (H, W, 3) and dtype uint8.

        Returns:
            PIL Image in RGB mode.

        Raises:
            ImageProcessingError: If conversion fails.

        Example:
            >>> arr = np.zeros((100, 100, 3), dtype=np.uint8)
            >>> loader = ImageLoader()
            >>> image = loader.from_numpy(arr)
            >>> print(image.size)
            (100, 100)
        """
        try:
            image = Image.fromarray(array)
            logger.debug(f"Converted numpy array to image: {array.shape}")
            return image
        except Exception as e:
            logger.error(f"Failed to convert numpy to image: {e}")
            raise ImageProcessingError(
                f"Failed to convert numpy array to image: {e}", original_error=e
            )

    def get_metadata(self, image: Image.Image) -> dict[str, Any]:
        """Get metadata about an image.

        Args:
            image: PIL Image to analyze.

        Returns:
            Dictionary containing image metadata.

        Example:
            >>> loader = ImageLoader()
            >>> image = loader.load(Path("photo.jpg"))
            >>> meta = loader.get_metadata(image)
            >>> print(meta["size"])
            (1920, 1080)
        """
        metadata = {
            "size": image.size,
            "mode": image.mode,
            "format": image.format,
            "width": image.width,
            "height": image.height,
        }

        # Add EXIF data if available
        if hasattr(image, "info") and image.info:
            metadata["info"] = {
                k: str(v) for k, v in image.info.items() if isinstance(v, (str, int, float, bool))
            }

        logger.debug(f"Image metadata: {metadata}")
        return metadata
