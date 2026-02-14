"""Performance benchmarks for CVD Simulator.

This module contains benchmarks for measuring the performance
of various CVD simulation operations.
"""

from __future__ import annotations

import pytest
from PIL import Image

from cvd_simulator import CVDSimulator, SimulationConfig
from cvd_simulator.core.simulator import AsyncCVDSimulator
from cvd_simulator.enums import Algorithm, CVDType


class TestAlgorithmPerformance:
    """Benchmarks for different simulation algorithms."""

    @pytest.mark.benchmark(group="algorithms")
    def test_brettel_1997_performance(self, benchmark, sample_image):
        """Benchmark Brettel 1997 algorithm."""
        config = SimulationConfig(algorithm=Algorithm.BRETTEL_1997)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="algorithms")
    def test_vienot_1999_performance(self, benchmark, sample_image):
        """Benchmark Viénot 1999 algorithm."""
        config = SimulationConfig(algorithm=Algorithm.VIENOT_1999)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="algorithms")
    def test_machado_2009_performance(self, benchmark, sample_image):
        """Benchmark Machado 2009 algorithm."""
        config = SimulationConfig(algorithm=Algorithm.MACHADO_2009)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="algorithms")
    def test_vischeck_performance(self, benchmark, sample_image):
        """Benchmark Vischeck algorithm."""
        config = SimulationConfig(algorithm=Algorithm.VISCHECK)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="algorithms")
    def test_auto_performance(self, benchmark, sample_image):
        """Benchmark Auto-select algorithm."""
        config = SimulationConfig(algorithm=Algorithm.AUTO)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None


class TestCVDTypePerformance:
    """Benchmarks for different CVD types."""

    @pytest.mark.benchmark(group="cvd_types")
    def test_protan_performance(self, benchmark, sample_image):
        """Benchmark protan simulation."""
        simulator = CVDSimulator()
        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="cvd_types")
    def test_deutan_performance(self, benchmark, sample_image):
        """Benchmark deutan simulation."""
        simulator = CVDSimulator()
        result = benchmark(simulator.simulate, sample_image, CVDType.DEUTAN)
        assert result is not None

    @pytest.mark.benchmark(group="cvd_types")
    def test_tritan_performance(self, benchmark, sample_image):
        """Benchmark tritan simulation."""
        simulator = CVDSimulator()
        result = benchmark(simulator.simulate, sample_image, CVDType.TRITAN)
        assert result is not None

    @pytest.mark.benchmark(group="cvd_types")
    def test_grayscale_performance(self, benchmark, sample_image):
        """Benchmark grayscale conversion."""
        simulator = CVDSimulator()
        result = benchmark(simulator.simulate, sample_image, CVDType.GRAYSCALE)
        assert result is not None


class TestImageSizePerformance:
    """Benchmarks for different image sizes."""

    @pytest.mark.benchmark(group="image_sizes")
    def test_small_image_100x100(self, benchmark):
        """Benchmark 100x100 image processing."""
        image = Image.new("RGB", (100, 100), color=(128, 64, 32))
        simulator = CVDSimulator()

        result = benchmark(simulator.simulate, image, CVDType.PROTAN)
        assert result.size == (100, 100)

    @pytest.mark.benchmark(group="image_sizes")
    def test_medium_image_500x500(self, benchmark):
        """Benchmark 500x500 image processing."""
        image = Image.new("RGB", (500, 500), color=(128, 64, 32))
        simulator = CVDSimulator()

        result = benchmark(simulator.simulate, image, CVDType.PROTAN)
        assert result.size == (500, 500)

    @pytest.mark.benchmark(group="image_sizes")
    def test_large_image_1000x1000(self, benchmark):
        """Benchmark 1000x1000 image processing."""
        image = Image.new("RGB", (1000, 1000), color=(128, 64, 32))
        simulator = CVDSimulator()

        result = benchmark(simulator.simulate, image, CVDType.PROTAN)
        assert result.size == (1000, 1000)


class TestBatchProcessingPerformance:
    """Benchmarks for batch processing operations."""

    @pytest.mark.benchmark(group="batch_processing")
    def test_sequential_batch_5_images(self, benchmark, tmp_path):
        """Benchmark sequential batch processing of 5 images."""
        # Create test images
        image_paths = []
        for i in range(5):
            img_path = tmp_path / f"test_{i}.png"
            img = Image.new("RGB", (200, 200), color=(i * 50, 100, 150))
            img.save(img_path)
            image_paths.append(img_path)

        simulator = CVDSimulator()

        def process_batch():
            return simulator.process_batch(image_paths)

        result = benchmark(process_batch)
        assert len(result) == 5

    @pytest.mark.benchmark(group="batch_processing")
    def test_parallel_batch_5_images(self, benchmark, tmp_path):
        """Benchmark parallel batch processing of 5 images."""
        # Create test images
        image_paths = []
        for i in range(5):
            img_path = tmp_path / f"test_{i}.png"
            img = Image.new("RGB", (200, 200), color=(i * 50, 100, 150))
            img.save(img_path)
            image_paths.append(img_path)

        simulator = AsyncCVDSimulator(max_workers=2)

        def process_batch_parallel():
            return simulator.process_batch_parallel(image_paths)

        result = benchmark(process_batch_parallel)
        assert len(result) == 5


class TestSeverityPerformance:
    """Benchmarks for different severity levels."""

    @pytest.mark.benchmark(group="severity")
    def test_severity_0_0(self, benchmark, sample_image):
        """Benchmark severity 0.0 (no deficiency)."""
        config = SimulationConfig(severity=0.0)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="severity")
    def test_severity_0_5(self, benchmark, sample_image):
        """Benchmark severity 0.5 (moderate)."""
        config = SimulationConfig(severity=0.5)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None

    @pytest.mark.benchmark(group="severity")
    def test_severity_1_0(self, benchmark, sample_image):
        """Benchmark severity 1.0 (complete deficiency)."""
        config = SimulationConfig(severity=1.0)
        simulator = CVDSimulator(config)

        result = benchmark(simulator.simulate, sample_image, CVDType.PROTAN)
        assert result is not None


class TestFullPipelinePerformance:
    """Benchmarks for complete processing pipeline."""

    @pytest.mark.benchmark(group="full_pipeline")
    def test_process_image_all_types(self, benchmark, sample_image_path):
        """Benchmark processing single image for all CVD types."""
        simulator = CVDSimulator()

        result = benchmark(simulator.process_image, sample_image_path)
        assert len(result) == 4  # 4 CVD types

    @pytest.mark.benchmark(group="full_pipeline")
    def test_process_image_single_type(self, benchmark, sample_image_path):
        """Benchmark processing single image for one CVD type."""
        simulator = CVDSimulator()
        image = simulator.loader.load(sample_image_path)

        def process_single():
            simulated = simulator.simulate(image, CVDType.PROTAN)
            return simulator.writer.save(simulated, CVDType.PROTAN)

        result = benchmark(process_single)
        assert result.exists()


class TestMemoryPerformance:
    """Benchmarks for memory usage patterns."""

    @pytest.mark.benchmark(group="memory")
    def test_numpy_conversion(self, benchmark, sample_image):
        """Benchmark numpy array conversion."""
        from cvd_simulator.core.image_loader import ImageLoader

        loader = ImageLoader()

        result = benchmark(loader.to_numpy, sample_image)
        assert result.shape == (100, 100, 3)

    @pytest.mark.benchmark(group="memory")
    def test_image_from_numpy(self, benchmark):
        """Benchmark image creation from numpy."""
        import numpy as np
        from cvd_simulator.core.image_loader import ImageLoader

        arr = np.zeros((100, 100, 3), dtype=np.uint8)
        arr[:, :] = [255, 128, 64]
        loader = ImageLoader()

        result = benchmark(loader.from_numpy, arr)
        assert result.size == (100, 100)


class TestConfigurationPerformance:
    """Benchmarks for configuration operations."""

    @pytest.mark.benchmark(group="configuration")
    def test_config_creation(self, benchmark):
        """Benchmark configuration creation."""
        result = benchmark(SimulationConfig)
        assert result is not None

    @pytest.mark.benchmark(group="configuration")
    def test_config_to_dict(self, benchmark):
        """Benchmark configuration serialization."""
        config = SimulationConfig()
        result = benchmark(config.to_dict)
        assert "severity" in result

    @pytest.mark.benchmark(group="configuration")
    def test_config_from_dict(self, benchmark):
        """Benchmark configuration deserialization."""
        data = {"algorithm": "MACHADO_2009", "severity": 0.7, "output_format": "PNG"}
        result = benchmark(SimulationConfig.from_dict, data)
        assert result.algorithm == Algorithm.MACHADO_2009
