"""pytest configuration and fixtures for CVD Simulator tests."""

from __future__ import annotations
from pathlib import Path

import pytest
from PIL import Image

from cvd_simulator import CVDSimulator, SimulationConfig
from cvd_simulator.enums import Algorithm, CVDType, OutputFormat
from cvd_simulator.utils.validators import SecurityValidator


@pytest.fixture
def temp_output_dir(tmp_path: Path) -> Path:
    """Provide a temporary output directory."""
    output_dir = tmp_path / "outputs"
    output_dir.mkdir()
    return output_dir


@pytest.fixture
def sample_image() -> Image.Image:
    """Create a sample RGB image for testing."""
    return Image.new('RGB', (100, 100), color=(255, 128, 64))


@pytest.fixture
def sample_image_path(tmp_path: Path) -> Path:
    """Create a sample image file for testing."""
    image_path = tmp_path / "test_image.png"
    image = Image.new('RGB', (100, 100), color=(255, 128, 64))
    image.save(image_path)
    return image_path


@pytest.fixture
def sample_images_dir(tmp_path: Path) -> Path:
    """Create a directory with multiple sample images."""
    img_dir = tmp_path / "images"
    img_dir.mkdir()
    
    # Create a few test images
    for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
        img = Image.new('RGB', (100, 100), color=color)
        img.save(img_dir / f"test_{i}.png")
    
    return img_dir


@pytest.fixture
def default_config(temp_output_dir: Path) -> SimulationConfig:
    """Provide a default configuration for testing."""
    return SimulationConfig(
        algorithm=Algorithm.BRETTEL_1997,
        severity=0.8,
        output_format=OutputFormat.PNG,
        output_directory=temp_output_dir,
    )


@pytest.fixture
def simulator(default_config: SimulationConfig) -> CVDSimulator:
    """Provide a configured simulator instance."""
    return CVDSimulator(default_config)


@pytest.fixture
def validator() -> SecurityValidator:
    """Provide a security validator instance."""
    return SecurityValidator(
        max_file_size=10 * 1024 * 1024,  # 10MB for tests
        max_dimension=1000,
    )


@pytest.fixture(params=list(Algorithm))
def all_algorithms(request) -> Algorithm:
    """Provide each algorithm for parameterized tests."""
    return request.param


@pytest.fixture(params=list(CVDType))
def all_cvd_types(request) -> CVDType:
    """Provide each CVD type for parameterized tests."""
    return request.param