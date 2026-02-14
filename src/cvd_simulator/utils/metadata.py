"""Metadata export utilities for reproducibility.

This module provides functionality to export simulation metadata as JSON sidecar files,
enabling full reproducibility of CVD simulation results.
"""

from __future__ import annotations

import hashlib
import json
import platform
import sys
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import TYPE_CHECKING, Any

from cvd_simulator.utils.logging_config import get_logger

if TYPE_CHECKING:
    from cvd_simulator.config import SimulationConfig
    from cvd_simulator.enums import CVDType

logger = get_logger(__name__)


@dataclass
class SimulationMetadata:
    """Metadata for a CVD simulation run.
    
    This class captures all information necessary to reproduce
    a simulation exactly, including software versions, configuration,
    and input file checksums.
    
    Attributes:
        version: CVD Simulator version.
        timestamp: ISO 8601 timestamp of the simulation.
        input_file: Path to the input file.
        input_checksum: SHA-256 checksum of input file.
        output_files: Dictionary mapping CVD types to output paths.
        config: Simulation configuration used.
        system_info: System information dictionary.
        execution_time_ms: Execution time in milliseconds.
        notes: Optional user notes.
    """
    version: str
    timestamp: str
    input_file: str
    input_checksum: str
    output_files: dict[str, str] = field(default_factory=dict)
    config: dict[str, Any] = field(default_factory=dict)
    system_info: dict[str, str] = field(default_factory=dict)
    execution_time_ms: float = 0.0
    notes: str = ""


def calculate_checksum(file_path: Path | str, algorithm: str = "sha256") -> str:
    """Calculate file checksum for integrity verification.
    
    Args:
        file_path: Path to the file.
        algorithm: Hash algorithm (sha256, md5, sha512).
    
    Returns:
        Hexadecimal checksum string.
    
    Raises:
        ValueError: If algorithm is not supported.
        FileNotFoundError: If file does not exist.
    """
    file_path = Path(file_path)
    
    if not file_path.exists():
        raise FileNotFoundError(f"File not found: {file_path}")
    
    hash_obj = hashlib.new(algorithm)
    
    # Read file in chunks to handle large files
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()


def get_system_info() -> dict[str, str]:
    """Get system information for reproducibility.
    
    Returns:
        Dictionary with system information.
    """
    info = {
        "platform": platform.platform(),
        "python_version": sys.version,
        "python_implementation": platform.python_implementation(),
        "processor": platform.processor() or "unknown",
        "machine": platform.machine(),
        "node": platform.node(),
    }
    
    # Add dependency versions if available
    try:
        from PIL import Image
        info["pillow_version"] = Image.__version__
    except Exception:
        info["pillow_version"] = "unknown"
    
    try:
        import numpy as np
        info["numpy_version"] = np.__version__
    except Exception:
        info["numpy_version"] = "unknown"
    
    try:
        from daltonlens import __version__ as daltonlens_version
        info["daltonlens_version"] = daltonlens_version
    except Exception:
        info["daltonlens_version"] = "unknown"
    
    return info


def create_metadata(
    input_file: Path | str,
    output_files: dict[CVDType, Path],
    config: SimulationConfig,
    execution_time_ms: float = 0.0,
    notes: str = ""
) -> SimulationMetadata:
    """Create metadata for a simulation run.
    
    Args:
        input_file: Path to the input image.
        output_files: Dictionary of CVD types to output paths.
        config: Simulation configuration used.
        execution_time_ms: Execution time in milliseconds.
        notes: Optional user notes.
    
    Returns:
        SimulationMetadata object.
    """
    from cvd_simulator import __version__
    
    input_path = Path(input_file)
    
    # Calculate input checksum
    try:
        input_checksum = calculate_checksum(input_path)
    except Exception as e:
        logger.warning(f"Could not calculate checksum: {e}")
        input_checksum = ""
    
    # Convert output files to strings
    output_dict = {
        cvd_type.name: str(path) for cvd_type, path in output_files.items()
    }
    
    metadata = SimulationMetadata(
        version=__version__,
        timestamp=datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        input_file=str(input_path),
        input_checksum=input_checksum,
        output_files=output_dict,
        config=config.to_dict(),
        system_info=get_system_info(),
        execution_time_ms=execution_time_ms,
        notes=notes
    )
    
    return metadata


def export_metadata(
    metadata: SimulationMetadata,
    output_path: Path | str,
    indent: int = 2
) -> Path:
    """Export metadata to a JSON sidecar file.
    
    Args:
        metadata: SimulationMetadata to export.
        output_path: Path for the output JSON file.
        indent: JSON indentation level.
    
    Returns:
        Path to the exported file.
    """
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Convert dataclass to dict
    data = {
        "version": metadata.version,
        "timestamp": metadata.timestamp,
        "input_file": metadata.input_file,
        "input_checksum": metadata.input_checksum,
        "output_files": metadata.output_files,
        "config": metadata.config,
        "system_info": metadata.system_info,
        "execution_time_ms": metadata.execution_time_ms,
        "notes": metadata.notes,
    }
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=indent, default=str)
    
    logger.info(f"Metadata exported: {output_path}")
    return output_path


def load_metadata(metadata_path: Path | str) -> SimulationMetadata:
    """Load metadata from a JSON sidecar file.
    
    Args:
        metadata_path: Path to the JSON metadata file.
    
    Returns:
        SimulationMetadata object.
    """
    metadata_path = Path(metadata_path)
    
    with open(metadata_path) as f:
        data = json.load(f)
    
    return SimulationMetadata(
        version=data["version"],
        timestamp=data["timestamp"],
        input_file=data["input_file"],
        input_checksum=data["input_checksum"],
        output_files=data.get("output_files", {}),
        config=data.get("config", {}),
        system_info=data.get("system_info", {}),
        execution_time_ms=data.get("execution_time_ms", 0.0),
        notes=data.get("notes", "")
    )


def verify_reproducibility(
    metadata_path: Path | str,
    input_file: Path | str | None = None
) -> dict[str, Any]:
    """Verify if a simulation can be reproduced.
    
    Args:
        metadata_path: Path to the metadata file.
        input_file: Optional input file to verify checksum against.
    
    Returns:
        Dictionary with verification results.
    """
    metadata = load_metadata(metadata_path)
    results = {
        "metadata_valid": True,
        "input_file_exists": False,
        "checksum_match": False,
        "software_version_match": False,
        "warnings": [],
        "errors": []
    }
    
    # Check input file
    if input_file is None:
        input_file = metadata.input_file
    
    input_path = Path(input_file)
    if input_path.exists():
        results["input_file_exists"] = True
        
        # Verify checksum
        try:
            current_checksum = calculate_checksum(input_path)
            if current_checksum == metadata.input_checksum:
                results["checksum_match"] = True
            else:
                results["errors"].append("Input file checksum does not match")
        except Exception as e:
            results["errors"].append(f"Could not verify checksum: {e}")
    else:
        results["errors"].append(f"Input file not found: {input_path}")
    
    # Check software version
    from cvd_simulator import __version__
    if metadata.version == __version__:
        results["software_version_match"] = True
    else:
        results["warnings"].append(
            f"Software version differs: metadata={metadata.version}, "
            f"current={__version__}"
        )
    
    # Check system compatibility
    current_system = get_system_info()
    if metadata.system_info.get("platform") != current_system["platform"]:
        results["warnings"].append(
            "Platform differs, results may vary slightly"
        )
    
    return results


def generate_sidecar_path(
    image_path: Path | str,
    suffix: str = "_metadata"
) -> Path:
    """Generate a sidecar metadata file path for an image.
    
    Args:
        image_path: Path to the image file.
        suffix: Suffix to add before the extension.
    
    Returns:
        Path for the metadata sidecar file.
    """
    image_path = Path(image_path)
    return image_path.parent / f"{image_path.stem}{suffix}.json"


__all__ = [
    "SimulationMetadata",
    "calculate_checksum",
    "get_system_info",
    "create_metadata",
    "export_metadata",
    "load_metadata",
    "verify_reproducibility",
    "generate_sidecar_path"
]
