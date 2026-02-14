"""CVD Simulator - Color Vision Deficiency Simulation Tool.

A comprehensive Python package for simulating color vision deficiencies
(protanopia, deuteranopia, tritanopia) using various scientific algorithms.

Example:
    >>> from cvd_simulator import CVDSimulator, SimulationConfig, CVDType
    >>> config = SimulationConfig(severity=0.8)
    >>> simulator = CVDSimulator(config)
    >>> result = simulator.simulate(image, CVDType.PROTAN)
"""

from cvd_simulator.core.simulator import CVDSimulator, AsyncCVDSimulator
from cvd_simulator.config import SimulationConfig
from cvd_simulator.enums import CVDType, Algorithm
from cvd_simulator.exceptions import (
    CVDSimulatorError,
    ImageProcessingError,
    SecurityError,
    ValidationError,
    ConfigurationError,
)

# Optional Pydantic config export
try:
    from cvd_simulator.config import SimulationConfigPydantic

    _has_pydantic = True
except ImportError:
    _has_pydantic = False

# v1.1.1 new exports
try:
    from cvd_simulator.presets import PresetType, Preset, get_preset, apply_preset

    _has_presets = True
except ImportError:
    _has_presets = False

try:
    from cvd_simulator.utils.metadata import SimulationMetadata, create_metadata, export_metadata

    _has_metadata = True
except ImportError:
    _has_metadata = False

try:
    from cvd_simulator.utils.profiling import PerformanceProfiler, Timer

    _has_profiling = True
except ImportError:
    _has_profiling = False

try:
    from cvd_simulator.core.video_processor import VideoProcessor, VideoMetadata

    _has_video = True
except ImportError:
    _has_video = False

__version__ = "1.1.1"
__author__ = "Michail Semoglou"

__all__ = [
    "CVDSimulator",
    "AsyncCVDSimulator",
    "SimulationConfig",
    "CVDType",
    "Algorithm",
    "CVDSimulatorError",
    "ImageProcessingError",
    "SecurityError",
    "ValidationError",
    "ConfigurationError",
]

# Add optional exports if available
if _has_pydantic:
    __all__.append("SimulationConfigPydantic")

if _has_presets:
    __all__.extend(["PresetType", "Preset", "get_preset", "apply_preset"])

if _has_metadata:
    __all__.extend(["SimulationMetadata", "create_metadata", "export_metadata"])

if _has_profiling:
    __all__.extend(["PerformanceProfiler", "Timer"])

if _has_video:
    __all__.extend(["VideoProcessor", "VideoMetadata"])
