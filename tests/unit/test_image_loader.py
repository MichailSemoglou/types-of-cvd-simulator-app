"""Unit tests for image loader."""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from cvd_simulator.core.image_loader import ImageLoader
from cvd_simulator.exceptions import ImageProcessingError


class TestImageLoader:
    """Tests for ImageLoader class."""

    def test_initialization(self):
        """Test loader initialization."""
        loader = ImageLoader()

        assert loader.validator is not None

    def test_load_valid_image(self, sample_image_path: Path):
        """Test loading a valid image."""
        loader = ImageLoader()

        image = loader.load(sample_image_path)

        assert isinstance(image, Image.Image)
        assert image.mode == "RGB"

    def test_load_nonexistent_file(self):
        """Test loading a non-existent file raises error."""
        loader = ImageLoader()

        with pytest.raises(ImageProcessingError):
            loader.load(Path("/nonexistent/file.png"))

    def test_load_invalid_file(self, tmp_path: Path):
        """Test loading an invalid file raises error."""
        loader = ImageLoader()

        invalid_file = tmp_path / "invalid.txt"
        invalid_file.write_text("not an image")

        with pytest.raises(ImageProcessingError):
            loader.load(invalid_file)

    def test_to_numpy(self, sample_image: Image.Image):
        """Test converting image to numpy array."""
        loader = ImageLoader()

        arr = loader.to_numpy(sample_image)

        assert isinstance(arr, np.ndarray)
        assert arr.shape == (100, 100, 3)
        assert arr.dtype == np.uint8

    def test_from_numpy(self):
        """Test converting numpy array to image."""
        loader = ImageLoader()

        arr = np.zeros((50, 50, 3), dtype=np.uint8)
        arr[:, :] = [255, 128, 64]

        image = loader.from_numpy(arr)

        assert isinstance(image, Image.Image)
        assert image.size == (50, 50)
        assert image.mode == "RGB"

    def test_get_metadata(self, sample_image: Image.Image):
        """Test getting image metadata."""
        loader = ImageLoader()
        sample_image.format = "PNG"

        metadata = loader.get_metadata(sample_image)

        assert metadata["size"] == (100, 100)
        assert metadata["mode"] == "RGB"
        assert metadata["width"] == 100
        assert metadata["height"] == 100

    def test_roundtrip_conversion(self, sample_image: Image.Image):
        """Test that image -> numpy -> image preserves data."""
        loader = ImageLoader()

        arr = loader.to_numpy(sample_image)
        recovered = loader.from_numpy(arr)

        assert recovered.size == sample_image.size
        assert recovered.mode == sample_image.mode
