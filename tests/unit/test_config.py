"""Unit tests for configuration module."""

from __future__ import annotations
from pathlib import Path

import pytest

from cvd_simulator.config import SimulationConfig
from cvd_simulator.enums import Algorithm, LogLevel, OutputFormat
from cvd_simulator.exceptions import ConfigurationError, ValidationError


class TestSimulationConfig:
    """Tests for SimulationConfig dataclass."""

    def test_default_values(self):
        """Test that default values are set correctly."""
        config = SimulationConfig()

        assert config.algorithm == Algorithm.BRETTEL_1997
        assert config.severity == 0.8
        assert config.output_format == OutputFormat.JPEG
        assert config.quality == 95
        assert config.optimize is True
        assert config.log_level == LogLevel.INFO

    def test_valid_severity_range(self):
        """Test that severity accepts valid values."""
        config = SimulationConfig(severity=0.0)
        assert config.severity == 0.0

        config = SimulationConfig(severity=1.0)
        assert config.severity == 1.0

        config = SimulationConfig(severity=0.5)
        assert config.severity == 0.5

    def test_invalid_severity_negative(self):
        """Test that negative severity raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationConfig(severity=-0.1)

        assert exc_info.value.field == "severity"
        assert exc_info.value.value == -0.1

    def test_invalid_severity_too_large(self):
        """Test that severity > 1.0 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationConfig(severity=1.5)

        assert exc_info.value.field == "severity"
        assert exc_info.value.value == 1.5

    def test_valid_quality_range(self):
        """Test that quality accepts valid values."""
        config = SimulationConfig(quality=1)
        assert config.quality == 1

        config = SimulationConfig(quality=95)
        assert config.quality == 95

    def test_invalid_quality_too_low(self):
        """Test that quality < 1 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationConfig(quality=0)

        assert exc_info.value.field == "quality"

    def test_invalid_quality_too_high(self):
        """Test that quality > 95 raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationConfig(quality=100)

        assert exc_info.value.field == "quality"

    def test_from_dict_valid(self):
        """Test creating config from valid dictionary."""
        data = {
            "algorithm": "MACHADO_2009",
            "severity": 0.7,
            "output_format": "PNG",
        }

        config = SimulationConfig.from_dict(data)

        assert config.algorithm == Algorithm.MACHADO_2009
        assert config.severity == 0.7
        assert config.output_format == OutputFormat.PNG

    def test_from_dict_unknown_key(self):
        """Test that unknown keys raise ConfigurationError."""
        data = {"unknown_key": "value"}

        with pytest.raises(ConfigurationError) as exc_info:
            SimulationConfig.from_dict(data)

        assert "unknown_key" in str(exc_info.value)

    def test_from_dict_invalid_algorithm(self):
        """Test that invalid algorithm raises ConfigurationError."""
        data = {"algorithm": "INVALID_ALGO"}

        with pytest.raises(ConfigurationError) as exc_info:
            SimulationConfig.from_dict(data)

        assert exc_info.value.config_key == "algorithm"

    def test_to_dict(self):
        """Test converting config to dictionary."""
        config = SimulationConfig(
            algorithm=Algorithm.VIENOT_1999,
            severity=0.9,
        )

        data = config.to_dict()

        assert data["algorithm"] == "VIENOT_1999"
        assert data["severity"] == 0.9
        assert isinstance(data["output_directory"], str)

    def test_from_env(self, monkeypatch):
        """Test creating config from environment variables."""
        monkeypatch.setenv("CVD_SIMULATOR_SEVERITY", "0.6")
        monkeypatch.setenv("CVD_SIMULATOR_QUALITY", "85")
        monkeypatch.setenv("CVD_SIMULATOR_ALGORITHM", "MACHADO_2009")

        config = SimulationConfig.from_env()

        assert config.severity == 0.6
        assert config.quality == 85
        assert config.algorithm == Algorithm.MACHADO_2009

    def test_output_directory_as_path(self):
        """Test that output_directory accepts Path object."""
        config = SimulationConfig(output_directory=Path("/tmp/outputs"))
        assert config.output_directory == Path("/tmp/outputs")

    def test_invalid_output_directory_type(self):
        """Test that invalid output_directory type raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            SimulationConfig(output_directory="/tmp/outputs")  # type: ignore

        assert exc_info.value.field == "output_directory"
