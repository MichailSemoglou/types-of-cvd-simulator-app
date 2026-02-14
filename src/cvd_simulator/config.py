"""Configuration management for the CVD Simulator application.

This module provides configuration classes and validation for the simulator,
allowing users to customize behavior through code, configuration files,
or environment variables.
"""

from __future__ import annotations
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

try:
    from pydantic import BaseModel, Field, field_validator
    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False

from cvd_simulator.enums import Algorithm, OutputFormat, LogLevel
from cvd_simulator.exceptions import ValidationError, ConfigurationError


@dataclass
class SimulationConfig:
    """Configuration for CVD simulation.
    
    This dataclass holds all configuration parameters for the simulator,
    with validation to ensure all values are within acceptable ranges.
    
    Attributes:
        algorithm: The simulation algorithm to use.
        severity: Severity of the deficiency simulation (0.0 to 1.0).
        output_format: Image format for output files.
        output_directory: Directory where output files will be saved.
        quality: JPEG/WebP quality setting (1-95).
        optimize: Whether to enable PIL optimization.
        log_level: Logging level for the application.
        max_workers: Maximum number of parallel workers for batch processing.
        max_image_size: Maximum allowed image file size in bytes.
        max_image_dimension: Maximum allowed image dimension in pixels.
    
    Example:
        >>> config = SimulationConfig(
        ...     algorithm=Algorithm.MACHADO_2009,
        ...     severity=0.8,
        ...     output_format=OutputFormat.PNG,
        ...     output_directory=Path("./outputs")
        ... )
        >>> print(config.algorithm)
        Algorithm.MACHADO_2009
    
    Raises:
        ValidationError: If any configuration value is invalid.
    """
    
    algorithm: Algorithm = field(default=Algorithm.BRETTEL_1997)
    severity: float = field(default=0.8)
    output_format: OutputFormat = field(default=OutputFormat.JPEG)
    output_directory: Path = field(
        default_factory=lambda: Path(os.getenv("CVD_SIMULATOR_OUTPUT_DIRECTORY", "./outputs"))
    )
    quality: int = field(default=95)
    optimize: bool = field(default=True)
    log_level: LogLevel = field(default=LogLevel.INFO)
    max_workers: int | None = field(default=None)
    max_image_size: int = field(default=100 * 1024 * 1024)  # 100MB
    max_image_dimension: int = field(default=10000)
    
    def __post_init__(self) -> None:
        """Validate configuration values after initialization."""
        self._validate()
    
    def _validate(self) -> None:
        """Validate all configuration values.
        
        Raises:
            ValidationError: If any value fails validation.
        """
        # Validate severity
        if not 0.0 <= self.severity <= 1.0:
            raise ValidationError(
                f"Severity must be between 0.0 and 1.0, got {self.severity}",
                field="severity",
                value=self.severity,
                constraint="0.0 <= severity <= 1.0"
            )
        
        # Validate quality
        if not 1 <= self.quality <= 95:
            raise ValidationError(
                f"Quality must be between 1 and 95, got {self.quality}",
                field="quality",
                value=self.quality,
                constraint="1 <= quality <= 95"
            )
        
        # Validate output directory
        if not isinstance(self.output_directory, Path):
            raise ValidationError(
                f"Output directory must be a Path object, got {type(self.output_directory)}",
                field="output_directory",
                value=self.output_directory,
                constraint="must be pathlib.Path"
            )
        
        # Validate max_workers
        if self.max_workers is not None and self.max_workers < 1:
            raise ValidationError(
                f"max_workers must be at least 1, got {self.max_workers}",
                field="max_workers",
                value=self.max_workers,
                constraint="max_workers >= 1"
            )
        
        # Validate max_image_size
        if self.max_image_size < 1:
            raise ValidationError(
                f"max_image_size must be positive, got {self.max_image_size}",
                field="max_image_size",
                value=self.max_image_size,
                constraint="max_image_size > 0"
            )
        
        # Validate max_image_dimension
        if self.max_image_dimension < 1:
            raise ValidationError(
                f"max_image_dimension must be positive, got {self.max_image_dimension}",
                field="max_image_dimension",
                value=self.max_image_dimension,
                constraint="max_image_dimension > 0"
            )
    
    @classmethod
    def from_dict(cls, config_dict: dict[str, Any]) -> SimulationConfig:
        """Create configuration from a dictionary.
        
        Args:
            config_dict: Dictionary containing configuration values.
        
        Returns:
            New SimulationConfig instance.
        
        Raises:
            ValidationError: If any value is invalid.
            ConfigurationError: If dictionary contains unknown keys.
        
        Example:
            >>> config = SimulationConfig.from_dict({
            ...     "algorithm": "MACHADO_2009",
            ...     "severity": 0.7,
            ...     "output_format": "PNG"
            ... })
        """
        # Create a copy to avoid modifying input
        data = config_dict.copy()
        
        # Convert enum strings to enum values
        if "algorithm" in data and isinstance(data["algorithm"], str):
            try:
                data["algorithm"] = Algorithm[data["algorithm"].upper()]
            except KeyError:
                raise ConfigurationError(
                    f"Unknown algorithm: {data['algorithm']}",
                    config_key="algorithm"
                )
        
        if "output_format" in data and isinstance(data["output_format"], str):
            try:
                data["output_format"] = OutputFormat[data["output_format"].upper()]
            except KeyError:
                raise ConfigurationError(
                    f"Unknown output format: {data['output_format']}",
                    config_key="output_format"
                )
        
        if "log_level" in data and isinstance(data["log_level"], str):
            try:
                data["log_level"] = LogLevel[data["log_level"].upper()]
            except KeyError:
                raise ConfigurationError(
                    f"Unknown log level: {data['log_level']}",
                    config_key="log_level"
                )
        
        # Convert path strings to Path objects
        if "output_directory" in data and isinstance(data["output_directory"], str):
            data["output_directory"] = Path(data["output_directory"])
        
        # Filter out unknown keys
        valid_keys = {f.name for f in cls.__dataclass_fields__.values()}
        unknown_keys = set(data.keys()) - valid_keys
        if unknown_keys:
            raise ConfigurationError(
                f"Unknown configuration keys: {unknown_keys}",
                config_key=list(unknown_keys)[0]
            )
        
        return cls(**data)
    
    @classmethod
    def from_env(cls) -> SimulationConfig:
        """Create configuration from environment variables.
        
        Environment variables are prefixed with 'CVD_SIMULATOR_':
        - CVD_SIMULATOR_ALGORITHM
        - CVD_SIMULATOR_SEVERITY
        - CVD_SIMULATOR_OUTPUT_FORMAT
        - CVD_SIMULATOR_OUTPUT_DIRECTORY
        - CVD_SIMULATOR_QUALITY
        - CVD_SIMULATOR_OPTIMIZE
        - CVD_SIMULATOR_LOG_LEVEL
        - CVD_SIMULATOR_MAX_WORKERS
        - CVD_SIMULATOR_MAX_IMAGE_SIZE
        - CVD_SIMULATOR_MAX_IMAGE_DIMENSION
        
        Returns:
            New SimulationConfig instance with values from environment.
        
        Example:
            >>> import os
            >>> os.environ["CVD_SIMULATOR_SEVERITY"] = "0.7"
            >>> config = SimulationConfig.from_env()
        """
        config_dict: dict[str, Any] = {}
        
        # String values
        if env_val := os.getenv("CVD_SIMULATOR_ALGORITHM"):
            config_dict["algorithm"] = env_val
        if env_val := os.getenv("CVD_SIMULATOR_OUTPUT_FORMAT"):
            config_dict["output_format"] = env_val
        if env_val := os.getenv("CVD_SIMULATOR_OUTPUT_DIRECTORY"):
            config_dict["output_directory"] = env_val
        if env_val := os.getenv("CVD_SIMULATOR_LOG_LEVEL"):
            config_dict["log_level"] = env_val
        
        # Float values
        env_val = os.getenv("CVD_SIMULATOR_SEVERITY")
        if env_val is not None:
            config_dict["severity"] = float(env_val)
        
        # Integer values
        env_val = os.getenv("CVD_SIMULATOR_QUALITY")
        if env_val is not None:
            config_dict["quality"] = int(env_val)
        env_val = os.getenv("CVD_SIMULATOR_MAX_WORKERS")
        if env_val is not None:
            config_dict["max_workers"] = int(env_val)
        env_val = os.getenv("CVD_SIMULATOR_MAX_IMAGE_SIZE")
        if env_val is not None:
            config_dict["max_image_size"] = int(env_val)
        env_val = os.getenv("CVD_SIMULATOR_MAX_IMAGE_DIMENSION")
        if env_val is not None:
            config_dict["max_image_dimension"] = int(env_val)
        
        # Boolean values
        env_val = os.getenv("CVD_SIMULATOR_OPTIMIZE")
        if env_val is not None:
            config_dict["optimize"] = env_val.lower() in ("true", "1", "yes", "on")
        
        return cls.from_dict(config_dict)
    
    def to_dict(self) -> dict[str, Any]:
        """Convert configuration to a dictionary.
        
        Returns:
            Dictionary representation of the configuration.
        
        Example:
            >>> config = SimulationConfig()
            >>> config_dict = config.to_dict()
            >>> print(config_dict["severity"])
            0.8
        """
        return {
            "algorithm": self.algorithm.name,
            "severity": self.severity,
            "output_format": self.output_format.name,
            "output_directory": str(self.output_directory),
            "quality": self.quality,
            "optimize": self.optimize,
            "log_level": self.log_level.name,
            "max_workers": self.max_workers,
            "max_image_size": self.max_image_size,
            "max_image_dimension": self.max_image_dimension,
        }


if PYDANTIC_AVAILABLE:
    class SimulationConfigPydantic(BaseModel):
        """Pydantic-based configuration for CVD simulation.
        
        This is an alternative configuration class that uses Pydantic
        for automatic validation. It provides the same functionality
        as SimulationConfig but with schema generation capabilities.
        
        Attributes:
            algorithm: The simulation algorithm to use.
            severity: Severity of the deficiency simulation (0.0 to 1.0).
            output_format: Image format for output files.
            output_directory: Directory where output files will be saved.
            quality: JPEG/WebP quality setting (1-95).
            optimize: Whether to enable PIL optimization.
            log_level: Logging level for the application.
            max_workers: Maximum number of parallel workers.
            max_image_size: Maximum allowed image file size in bytes.
            max_image_dimension: Maximum allowed image dimension in pixels.
        
        Example:
            >>> config = SimulationConfigPydantic(
            ...     algorithm=Algorithm.MACHADO_2009,
            ...     severity=0.8
            ... )
            >>> print(config.model_dump_json())
        """
        
        model_config = {"arbitrary_types_allowed": True}
        
        algorithm: Algorithm = Field(default=Algorithm.BRETTEL_1997)
        severity: float = Field(default=0.8, ge=0.0, le=1.0)
        output_format: OutputFormat = Field(default=OutputFormat.JPEG)
        output_directory: Path = Field(default_factory=lambda: Path("./outputs"))
        quality: int = Field(default=95, ge=1, le=95)
        optimize: bool = Field(default=True)
        log_level: LogLevel = Field(default=LogLevel.INFO)
        max_workers: int | None = Field(default=None, ge=1)
        max_image_size: int = Field(default=100 * 1024 * 1024, gt=0)
        max_image_dimension: int = Field(default=10000, gt=0)
        
        @field_validator("output_directory", mode="before")
        @classmethod
        def validate_output_directory(cls, v: Any) -> Path:
            """Convert string paths to Path objects."""
            if isinstance(v, str):
                return Path(v)
            return v
        
        def to_simulation_config(self) -> SimulationConfig:
            """Convert to standard SimulationConfig.
            
            Returns:
                SimulationConfig instance with same values.
            """
            return SimulationConfig(
                algorithm=self.algorithm,
                severity=self.severity,
                output_format=self.output_format,
                output_directory=self.output_directory,
                quality=self.quality,
                optimize=self.optimize,
                log_level=self.log_level,
                max_workers=self.max_workers,
                max_image_size=self.max_image_size,
                max_image_dimension=self.max_image_dimension,
            )
        
        @classmethod
        def from_simulation_config(cls, config: SimulationConfig) -> SimulationConfigPydantic:
            """Create from standard SimulationConfig.
            
            Args:
                config: SimulationConfig to convert.
            
            Returns:
                SimulationConfigPydantic instance.
            """
            return cls(**config.to_dict())
    
    # Add to exports if Pydantic is available
    __all__ = ["SimulationConfig", "SimulationConfigPydantic"]
else:
    __all__ = ["SimulationConfig"]