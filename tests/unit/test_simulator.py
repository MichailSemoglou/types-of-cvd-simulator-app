"""Unit tests for the CVDSimulator class."""

from __future__ import annotations
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

from cvd_simulator import CVDSimulator, SimulationConfig
from cvd_simulator.enums import Algorithm, CVDType, OutputFormat
from cvd_simulator.exceptions import CVDSimulatorError


class TestCVDSimulator:
    """Tests for CVDSimulator class."""
    
    def test_initialization(self, default_config: SimulationConfig):
        """Test simulator initialization."""
        simulator = CVDSimulator(default_config)
        
        assert simulator.config == default_config
        assert simulator.loader is not None
        assert simulator.writer is not None
        assert simulator._simulator is not None
    
    def test_initialization_default_config(self):
        """Test simulator initialization with default config."""
        simulator = CVDSimulator()
        
        assert simulator.config is not None
        assert simulator.config.algorithm == Algorithm.BRETTEL_1997
    
    def test_simulate_protan(self, simulator: CVDSimulator, sample_image: Image.Image):
        """Test protan simulation produces valid output."""
        result = simulator.simulate(sample_image, CVDType.PROTAN)
        
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        assert result.mode == 'RGB'
    
    def test_simulate_deutan(self, simulator: CVDSimulator, sample_image: Image.Image):
        """Test deutan simulation produces valid output."""
        result = simulator.simulate(sample_image, CVDType.DEUTAN)
        
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        assert result.mode == 'RGB'
    
    def test_simulate_tritan(self, simulator: CVDSimulator, sample_image: Image.Image):
        """Test tritan simulation produces valid output."""
        result = simulator.simulate(sample_image, CVDType.TRITAN)
        
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        assert result.mode == 'RGB'
    
    def test_simulate_grayscale(self, simulator: CVDSimulator, sample_image: Image.Image):
        """Test grayscale conversion."""
        result = simulator.simulate(sample_image, CVDType.GRAYSCALE)
        
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
        assert result.mode == 'RGB'
        
        # Convert to numpy and check if all channels are equal (grayscale)
        arr = np.array(result)
        assert np.allclose(arr[:,:,0], arr[:,:,1])
        assert np.allclose(arr[:,:,1], arr[:,:,2])
    
    def test_simulate_all_types(self, simulator: CVDSimulator, sample_image: Image.Image):
        """Test simulation for all CVD types."""
        for cvd_type in CVDType:
            result = simulator.simulate(sample_image, cvd_type)
            assert isinstance(result, Image.Image)
            assert result.size == sample_image.size
    
    def test_process_image_creates_outputs(
        self, 
        simulator: CVDSimulator, 
        sample_image_path: Path,
        temp_output_dir: Path
    ):
        """Test that process_image creates all output files."""
        results = simulator.process_image(sample_image_path)
        
        assert len(results) == len(CVDType)
        
        for cvd_type, output_path in results.items():
            assert output_path.exists()
            assert output_path.stat().st_size > 0
    
    def test_different_algorithms_produce_output(
        self,
        sample_image: Image.Image,
        all_algorithms: Algorithm
    ):
        """Test that all algorithms produce valid output."""
        config = SimulationConfig(algorithm=all_algorithms)
        simulator = CVDSimulator(config)
        
        result = simulator.simulate(sample_image, CVDType.DEUTAN)
        assert isinstance(result, Image.Image)
        assert result.size == sample_image.size
    
    def test_get_supported_algorithms(self, simulator: CVDSimulator):
        """Test get_supported_algorithms returns all algorithms."""
        algorithms = simulator.get_supported_algorithms()
        
        assert len(algorithms) == len(Algorithm)
        assert all(isinstance(a, Algorithm) for a in algorithms)
    
    def test_get_supported_cvd_types(self, simulator: CVDSimulator):
        """Test get_supported_cvd_types returns all types."""
        types = simulator.get_supported_cvd_types()
        
        assert len(types) == len(CVDType)
        assert all(isinstance(t, CVDType) for t in types)
    
    def test_batch_process_empty_list(self, simulator: CVDSimulator):
        """Test batch processing with empty list."""
        results = simulator.process_batch([])
        
        assert results == {}
    
    def test_batch_process_single_image(
        self,
        simulator: CVDSimulator,
        sample_image_path: Path
    ):
        """Test batch processing with single image."""
        results = simulator.process_batch([sample_image_path])
        
        assert len(results) == 1
        assert sample_image_path in results
        assert results[sample_image_path] is not None
    
    def test_batch_process_multiple_images(
        self,
        simulator: CVDSimulator,
        sample_images_dir: Path
    ):
        """Test batch processing with multiple images."""
        image_paths = list(sample_images_dir.glob("*.png"))
        results = simulator.process_batch(image_paths)
        
        assert len(results) == len(image_paths)
        assert all(results[path] is not None for path in image_paths)