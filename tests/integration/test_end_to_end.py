"""End-to-end integration tests for the CVD Simulator."""

from __future__ import annotations
from pathlib import Path

import pytest
from PIL import Image

from cvd_simulator import CVDSimulator, SimulationConfig
from cvd_simulator.enums import Algorithm, CVDType, OutputFormat


class TestEndToEnd:
    """End-to-end integration tests."""

    def test_single_image_processing(self, tmp_path: Path):
        """Test processing a single image through the full pipeline."""
        # Setup
        input_image = tmp_path / "input.png"
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        # Create test image
        img = Image.new("RGB", (200, 200), color=(100, 150, 200))
        img.save(input_image)

        # Configure and run
        config = SimulationConfig(
            algorithm=Algorithm.BRETTEL_1997,
            severity=0.8,
            output_format=OutputFormat.PNG,
            output_directory=output_dir,
        )

        simulator = CVDSimulator(config)
        results = simulator.process_image(input_image)

        # Verify
        assert len(results) == len(CVDType)

        for cvd_type, output_path in results.items():
            assert output_path.exists(), f"Output for {cvd_type.name} not found"
            assert output_path.stat().st_size > 0

            # Verify image can be loaded
            result_img = Image.open(output_path)
            assert result_img.mode == "RGB"
            assert result_img.size == (200, 200)

    def test_batch_processing(self, tmp_path: Path):
        """Test batch processing multiple images."""
        # Setup
        input_dir = tmp_path / "inputs"
        input_dir.mkdir()
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        # Create multiple test images
        image_paths = []
        for i, color in enumerate([(255, 0, 0), (0, 255, 0), (0, 0, 255)]):
            img_path = input_dir / f"test_{i}.png"
            img = Image.new("RGB", (100, 100), color=color)
            img.save(img_path)
            image_paths.append(img_path)

        # Configure and run
        config = SimulationConfig(
            output_format=OutputFormat.PNG,
            output_directory=output_dir,
        )

        simulator = CVDSimulator(config)
        results = simulator.process_batch(image_paths)

        # Verify
        assert len(results) == len(image_paths)

        for img_path, result in results.items():
            assert result is not None, f"Processing failed for {img_path}"
            assert len(result) == len(CVDType)

    def test_all_algorithms(self, tmp_path: Path):
        """Test that all algorithms produce valid output."""
        input_image = tmp_path / "input.png"
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        img = Image.new("RGB", (100, 100), color=(128, 128, 128))
        img.save(input_image)

        for algorithm in Algorithm:
            config = SimulationConfig(
                algorithm=algorithm,
                output_format=OutputFormat.PNG,
                output_directory=output_dir / algorithm.name.lower(),
            )

            simulator = CVDSimulator(config)
            results = simulator.process_image(input_image)

            # Verify all outputs exist
            for output_path in results.values():
                assert output_path.exists(), f"Failed for algorithm {algorithm.name}"

    def test_different_output_formats(self, tmp_path: Path):
        """Test that all output formats work correctly."""
        input_image = tmp_path / "input.png"
        output_dir = tmp_path / "outputs"
        output_dir.mkdir()

        img = Image.new("RGB", (100, 100), color=(200, 100, 50))
        img.save(input_image)

        for fmt in OutputFormat:
            config = SimulationConfig(
                output_format=fmt,
                output_directory=output_dir / fmt.name.lower(),
            )

            simulator = CVDSimulator(config)
            results = simulator.process_image(input_image)

            # Verify output has correct extension
            for output_path in results.values():
                assert output_path.suffix == f".{fmt.value}"
                assert output_path.exists()
