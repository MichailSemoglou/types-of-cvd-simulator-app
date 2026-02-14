"""Unit tests for the metadata export system."""

import json
import pytest
import tempfile
from pathlib import Path
from PIL import Image

from cvd_simulator.utils.metadata import (
    SimulationMetadata,
    calculate_checksum,
    get_system_info,
    create_metadata,
    export_metadata,
    load_metadata,
    verify_reproducibility,
    generate_sidecar_path,
)
from cvd_simulator.config import SimulationConfig
from cvd_simulator.enums import CVDType


class TestCalculateChecksum:
    """Tests for calculate_checksum function."""
    
    def test_calculate_checksum_sha256(self, tmp_path):
        """Test SHA-256 checksum calculation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        checksum = calculate_checksum(test_file)
        assert len(checksum) == 64  # SHA-256 produces 64 hex chars
        assert all(c in "0123456789abcdef" for c in checksum)
    
    def test_calculate_checksum_md5(self, tmp_path):
        """Test MD5 checksum calculation."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Hello, World!")
        
        checksum = calculate_checksum(test_file, algorithm="md5")
        assert len(checksum) == 32  # MD5 produces 32 hex chars
    
    def test_calculate_checksum_file_not_found(self):
        """Test error on missing file."""
        with pytest.raises(FileNotFoundError):
            calculate_checksum("/nonexistent/file.txt")
    
    def test_calculate_checksum_consistency(self, tmp_path):
        """Test checksum is consistent for same content."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("Consistent content")
        
        checksum1 = calculate_checksum(test_file)
        checksum2 = calculate_checksum(test_file)
        assert checksum1 == checksum2


class TestGetSystemInfo:
    """Tests for get_system_info function."""
    
    def test_system_info_structure(self):
        """Test system info contains expected keys."""
        info = get_system_info()
        
        assert "platform" in info
        assert "python_version" in info
        assert "python_implementation" in info
        assert "machine" in info
        assert "pillow_version" in info
        assert "numpy_version" in info
    
    def test_system_info_values(self):
        """Test system info values are non-empty strings."""
        info = get_system_info()
        
        for key, value in info.items():
            assert isinstance(value, str)
            assert len(value) > 0


class TestCreateMetadata:
    """Tests for create_metadata function."""
    
    def test_create_metadata_basic(self, tmp_path):
        """Test basic metadata creation."""
        # Create test image
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        
        config = SimulationConfig()
        output_files = {CVDType.PROTAN: tmp_path / "protan.png"}
        
        metadata = create_metadata(image_path, output_files, config)
        
        assert isinstance(metadata, SimulationMetadata)
        assert metadata.input_file == str(image_path)
        assert len(metadata.input_checksum) == 64
        assert metadata.config is not None
    
    def test_create_metadata_with_notes(self, tmp_path):
        """Test metadata creation with notes."""
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        
        config = SimulationConfig()
        output_files = {CVDType.PROTAN: tmp_path / "protan.png"}
        
        metadata = create_metadata(
            image_path, output_files, config,
            notes="Test notes"
        )
        
        assert metadata.notes == "Test notes"


class TestExportAndLoadMetadata:
    """Tests for export_metadata and load_metadata functions."""
    
    def test_export_and_load_metadata(self, tmp_path):
        """Test exporting and loading metadata."""
        # Create metadata
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        
        config = SimulationConfig()
        output_files = {CVDType.PROTAN: tmp_path / "protan.png"}
        
        metadata = create_metadata(image_path, output_files, config)
        
        # Export
        output_path = tmp_path / "metadata.json"
        export_metadata(metadata, output_path)
        
        assert output_path.exists()
        
        # Load
        loaded = load_metadata(output_path)
        
        assert loaded.input_file == metadata.input_file
        assert loaded.input_checksum == metadata.input_checksum
        assert loaded.version == metadata.version
    
    def test_export_creates_directory(self, tmp_path):
        """Test export creates parent directories."""
        metadata = SimulationMetadata(
            version="1.0.0",
            timestamp="2024-01-01T00:00:00Z",
            input_file="test.png",
            input_checksum="abc123"
        )
        
        output_path = tmp_path / "subdir" / "metadata.json"
        export_metadata(metadata, output_path)
        
        assert output_path.exists()


class TestVerifyReproducibility:
    """Tests for verify_reproducibility function."""
    
    def test_verify_reproducibility_success(self, tmp_path):
        """Test successful reproducibility verification."""
        # Create and save metadata
        image_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(image_path)
        
        config = SimulationConfig()
        output_files = {CVDType.PROTAN: tmp_path / "protan.png"}
        
        metadata = create_metadata(image_path, output_files, config)
        metadata_path = tmp_path / "metadata.json"
        export_metadata(metadata, metadata_path)
        
        # Verify
        results = verify_reproducibility(metadata_path)
        
        assert results["metadata_valid"] is True
        assert results["input_file_exists"] is True
        assert results["checksum_match"] is True
    
    def test_verify_reproducibility_missing_file(self, tmp_path):
        """Test verification with missing input file."""
        # Create metadata for non-existent file
        metadata = SimulationMetadata(
            version="1.0.0",
            timestamp="2024-01-01T00:00:00Z",
            input_file="/nonexistent/file.png",
            input_checksum="abc123"
        )
        metadata_path = tmp_path / "metadata.json"
        export_metadata(metadata, metadata_path)
        
        results = verify_reproducibility(metadata_path)
        
        assert results["input_file_exists"] is False
        assert len(results["errors"]) > 0


class TestGenerateSidecarPath:
    """Tests for generate_sidecar_path function."""
    
    def test_generate_sidecar_path_default(self):
        """Test default sidecar path generation."""
        image_path = Path("/path/to/image.png")
        sidecar = generate_sidecar_path(image_path)
        
        assert sidecar == Path("/path/to/image_metadata.json")
    
    def test_generate_sidecar_path_custom_suffix(self):
        """Test custom suffix sidecar path generation."""
        image_path = Path("/path/to/image.png")
        sidecar = generate_sidecar_path(image_path, suffix="_info")
        
        assert sidecar == Path("/path/to/image_info.json")
    
    def test_generate_sidecar_path_complex_name(self):
        """Test sidecar path with complex filename."""
        image_path = Path("/path/to/my.image.file.png")
        sidecar = generate_sidecar_path(image_path)
        
        assert sidecar == Path("/path/to/my.image.file_metadata.json")


class TestSimulationMetadataDataclass:
    """Tests for SimulationMetadata dataclass."""
    
    def test_metadata_defaults(self):
        """Test metadata default values."""
        metadata = SimulationMetadata(
            version="1.0.0",
            timestamp="2024-01-01T00:00:00Z",
            input_file="test.png",
            input_checksum="abc123"
        )
        
        assert metadata.output_files == {}
        assert metadata.config == {}
        assert metadata.system_info == {}
        assert metadata.execution_time_ms == 0.0
        assert metadata.notes == ""
