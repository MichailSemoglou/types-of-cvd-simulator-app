"""Property-based tests for CVD Simulator using Hypothesis.

This module contains property-based tests that verify invariants
and properties of the CVD simulation functions across a wide range
of inputs.
"""

from __future__ import annotations

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from PIL import Image

from cvd_simulator import CVDSimulator, SimulationConfig
from cvd_simulator.core.image_loader import ImageLoader
from cvd_simulator.enums import Algorithm, CVDType


class TestSimulationInvariants:
    """Property-based tests for simulation invariants."""

    @given(
        width=st.integers(min_value=1, max_value=500),
        height=st.integers(min_value=1, max_value=500),
        r=st.integers(min_value=0, max_value=255),
        g=st.integers(min_value=0, max_value=255),
        b=st.integers(min_value=0, max_value=255),
    )
    @settings(max_examples=50, deadline=5000)
    def test_output_dimensions_match_input(self, width, height, r, g, b):
        """Simulation should preserve image dimensions."""
        img = Image.new("RGB", (width, height), color=(r, g, b))
        simulator = CVDSimulator()

        result = simulator.simulate(img, CVDType.PROTAN)

        assert result.size == (width, height)
        assert result.mode == "RGB"

    @given(
        width=st.integers(min_value=1, max_value=300),
        height=st.integers(min_value=1, max_value=300),
    )
    @settings(max_examples=30, deadline=5000)
    def test_all_cvd_types_preserve_dimensions(self, width, height):
        """All CVD types should preserve image dimensions."""
        img = Image.new("RGB", (width, height), color=(128, 128, 128))
        simulator = CVDSimulator()

        for cvd_type in CVDType:
            result = simulator.simulate(img, cvd_type)
            assert result.size == (width, height), f"Failed for {cvd_type}"

    @given(
        width=st.integers(min_value=1, max_value=200),
        height=st.integers(min_value=1, max_value=200),
    )
    @settings(max_examples=20, deadline=5000)
    def test_all_algorithms_produce_valid_output(self, width, height):
        """All algorithms should produce valid output."""
        img = Image.new("RGB", (width, height), color=(100, 150, 200))

        for algorithm in Algorithm:
            config = SimulationConfig(algorithm=algorithm)
            simulator = CVDSimulator(config)
            result = simulator.simulate(img, CVDType.DEUTAN)

            assert isinstance(result, Image.Image)
            assert result.size == (width, height)
            assert result.mode == "RGB"


class TestGrayscaleProperties:
    """Property-based tests for grayscale conversion."""

    @given(
        width=st.integers(min_value=1, max_value=300),
        height=st.integers(min_value=1, max_value=300),
        r=st.integers(min_value=0, max_value=255),
        g=st.integers(min_value=0, max_value=255),
        b=st.integers(min_value=0, max_value=255),
    )
    @settings(max_examples=50, deadline=5000)
    def test_grayscale_has_equal_channels(self, width, height, r, g, b):
        """Grayscale conversion should produce equal RGB channels."""
        img = Image.new("RGB", (width, height), color=(r, g, b))
        simulator = CVDSimulator()

        result = simulator.simulate(img, CVDType.GRAYSCALE)
        arr = np.array(result)

        # All channels should be equal
        assert np.allclose(arr[:, :, 0], arr[:, :, 1])
        assert np.allclose(arr[:, :, 1], arr[:, :, 2])


class TestConfigurationProperties:
    """Property-based tests for configuration validation."""

    @given(severity=st.floats(min_value=0.0, max_value=1.0, allow_nan=False))
    @settings(max_examples=50)
    def test_valid_severity_always_creates_config(self, severity):
        """Valid severity should always create a config."""
        config = SimulationConfig(severity=severity)
        assert config.severity == pytest.approx(severity, abs=1e-10)

    @given(quality=st.integers(min_value=1, max_value=95))
    @settings(max_examples=50)
    def test_valid_quality_always_creates_config(self, quality):
        """Valid quality should always create a config."""
        config = SimulationConfig(quality=quality)
        assert config.quality == quality


class TestImageLoaderProperties:
    """Property-based tests for image loader operations."""

    @given(
        width=st.integers(min_value=1, max_value=500),
        height=st.integers(min_value=1, max_value=500),
        r=st.integers(min_value=0, max_value=255),
        g=st.integers(min_value=0, max_value=255),
        b=st.integers(min_value=0, max_value=255),
    )
    @settings(max_examples=30, deadline=5000)
    def test_numpy_roundtrip_preserves_data(self, width, height, r, g, b):
        """Converting to numpy and back should preserve image data."""
        original = Image.new("RGB", (width, height), color=(r, g, b))
        loader = ImageLoader()

        arr = loader.to_numpy(original)
        recovered = loader.from_numpy(arr)

        assert recovered.size == original.size
        assert recovered.mode == original.mode


class TestSeverityProperties:
    """Property-based tests for severity levels."""

    @given(
        severity=st.floats(min_value=0.0, max_value=1.0, allow_nan=False),
        width=st.integers(min_value=10, max_value=100),
        height=st.integers(min_value=10, max_value=100),
    )
    @settings(max_examples=30, deadline=5000)
    def test_severity_does_not_affect_dimensions(self, severity, width, height):
        """Different severity levels should not affect output dimensions."""
        img = Image.new("RGB", (width, height), color=(128, 64, 32))
        config = SimulationConfig(severity=severity)
        simulator = CVDSimulator(config)

        result = simulator.simulate(img, CVDType.PROTAN)

        assert result.size == (width, height)


class TestColorInvariants:
    """Property-based tests for color-related invariants."""

    @given(
        width=st.integers(min_value=1, max_value=100),
        height=st.integers(min_value=1, max_value=100),
        gray=st.integers(min_value=0, max_value=255),
    )
    @settings(max_examples=20, deadline=5000)
    def test_grayscale_image_stays_grayscale(self, width, height, gray):
        """Grayscale images should remain grayscale after any simulation."""
        img = Image.new("RGB", (width, height), color=(gray, gray, gray))
        simulator = CVDSimulator()

        for cvd_type in [CVDType.PROTAN, CVDType.DEUTAN, CVDType.TRITAN]:
            result = simulator.simulate(img, cvd_type)
            arr = np.array(result)

            # Check that channels are still equal (grayscale stays grayscale)
            assert np.allclose(arr[:, :, 0], arr[:, :, 1], atol=1)
            assert np.allclose(arr[:, :, 1], arr[:, :, 2], atol=1)


class TestOutputFormatProperties:
    """Property-based tests for output format behavior."""

    @given(
        width=st.integers(min_value=1, max_value=200),
        height=st.integers(min_value=1, max_value=200),
    )
    @settings(max_examples=20, deadline=10000)
    def test_saved_image_can_be_reloaded(self, width, height, tmp_path):
        """Saved images should be reloadable and have same dimensions."""
        from cvd_simulator.enums import OutputFormat

        img = Image.new("RGB", (width, height), color=(100, 150, 200))
        config = SimulationConfig(output_directory=tmp_path, output_format=OutputFormat.PNG)
        simulator = CVDSimulator(config)

        # Simulate and save
        result = simulator.simulate(img, CVDType.PROTAN)
        output_path = simulator.writer.save(result, CVDType.PROTAN)

        # Reload and verify
        reloaded = Image.open(output_path)
        assert reloaded.size == (width, height)


class TestBatchProcessingProperties:
    """Property-based tests for batch processing."""

    @given(
        num_images=st.integers(min_value=1, max_value=5),
        width=st.integers(min_value=10, max_value=100),
        height=st.integers(min_value=10, max_value=100),
    )
    @settings(max_examples=10, deadline=30000)
    def test_batch_returns_correct_number_of_results(self, num_images, width, height, tmp_path):
        """Batch processing should return result for each input."""
        image_paths = []
        for i in range(num_images):
            img_path = tmp_path / f"test_{i}.png"
            img = Image.new("RGB", (width, height), color=(i * 50, 100, 150))
            img.save(img_path)
            image_paths.append(img_path)

        simulator = CVDSimulator()
        results = simulator.process_batch(image_paths)

        assert len(results) == num_images


class TestAlgorithmConsistency:
    """Property-based tests for algorithm consistency."""

    @given(
        width=st.integers(min_value=1, max_value=100),
        height=st.integers(min_value=1, max_value=100),
        r=st.integers(min_value=0, max_value=255),
        g=st.integers(min_value=0, max_value=255),
        b=st.integers(min_value=0, max_value=255),
    )
    @settings(max_examples=10, deadline=10000)
    def test_auto_select_produces_valid_output(self, width, height, r, g, b):
        """Auto-select algorithm should always produce valid output."""
        img = Image.new("RGB", (width, height), color=(r, g, b))
        config = SimulationConfig(algorithm=Algorithm.AUTO)
        simulator = CVDSimulator(config)

        for cvd_type in CVDType:
            result = simulator.simulate(img, cvd_type)
            assert isinstance(result, Image.Image)
            assert result.size == (width, height)
            assert result.mode == "RGB"


# Custom strategy for generating valid RGB images
def rgb_image_strategy(max_size=100):
    """Generate PIL RGB images with random content."""
    return st.builds(
        lambda w, h, data: Image.frombytes("RGB", (w, h), bytes(data)),
        st.integers(min_value=1, max_value=max_size),
        st.integers(min_value=1, max_value=max_size),
        st.lists(
            st.integers(min_value=0, max_value=255), min_size=3, max_size=3 * max_size * max_size
        ),
    )
