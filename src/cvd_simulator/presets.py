"""Preset configurations for CVD Simulator.

This module provides predefined configuration profiles for common use cases,
allowing users to quickly apply optimized settings for specific domains.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

from cvd_simulator.config import SimulationConfig
from cvd_simulator.enums import Algorithm, OutputFormat


class PresetType(Enum):
    """Available preset configuration types.
    
    Each preset is optimized for a specific use case or domain.
    
    Attributes:
        WEB_DESIGN: Optimized for web UI/UX design and accessibility testing.
        PRINT_MEDIA: Optimized for print media and high-resolution output.
        SCIENTIFIC_VISUALIZATION: Optimized for data visualization and research.
        MOBILE_APP: Optimized for mobile application design.
        ARCHIVAL: Optimized for archival and preservation workflows.
        FAST_PREVIEW: Optimized for quick previews and iterative design.
    """
    WEB_DESIGN = "web_design"
    PRINT_MEDIA = "print_media"
    SCIENTIFIC_VISUALIZATION = "scientific_visualization"
    MOBILE_APP = "mobile_app"
    ARCHIVAL = "archival"
    FAST_PREVIEW = "fast_preview"


@dataclass
class Preset:
    """A preset configuration with metadata.
    
    Attributes:
        name: Display name for the preset.
        description: Detailed description of when to use this preset.
        config: The SimulationConfig to apply.
        recommended_for: List of use cases this preset is designed for.
    """
    name: str
    description: str
    config: SimulationConfig
    recommended_for: list[str] = field(default_factory=list)


# Preset definitions
PRESETS: dict[PresetType, Preset] = {
    PresetType.WEB_DESIGN: Preset(
        name="Web Design",
        description=(
            "Optimized for web UI/UX design and accessibility testing. "
            "Uses WebP format for modern browser compatibility, moderate quality "
            "for fast loading, and Machado 2009 algorithm for accurate severity simulation."
        ),
        config=SimulationConfig(
            algorithm=Algorithm.MACHADO_2009,
            severity=0.8,
            output_format=OutputFormat.WEBP,
            quality=85,
            optimize=True,
        ),
        recommended_for=[
            "Website accessibility audits",
            "UI/UX design validation",
            "Frontend development testing",
            "Browser compatibility checks"
        ]
    ),
    
    PresetType.PRINT_MEDIA: Preset(
        name="Print Media",
        description=(
            "Optimized for print media and high-resolution output. "
            "Uses PNG format for lossless quality, maximum output quality, "
            "and Viénot 1999 algorithm for severe deficiency accuracy."
        ),
        config=SimulationConfig(
            algorithm=Algorithm.VIENOT_1999,
            severity=1.0,
            output_format=OutputFormat.PNG,
            quality=95,
            optimize=True,
        ),
        recommended_for=[
            "Magazine and book design",
            "Poster and flyer creation",
            "Professional photography",
            "High-resolution artwork"
        ]
    ),
    
    PresetType.SCIENTIFIC_VISUALIZATION: Preset(
        name="Scientific Visualization",
        description=(
            "Optimized for data visualization and research applications. "
            "Uses TIFF format for archival quality, maximum severity for "
            "worst-case testing, and Brettel 1997 for computational efficiency "
            "in batch processing."
        ),
        config=SimulationConfig(
            algorithm=Algorithm.BRETTEL_1997,
            severity=1.0,
            output_format=OutputFormat.TIFF,
            quality=95,
            optimize=False,  # TIFF doesn't use the same optimization
        ),
        recommended_for=[
            "Research paper figures",
            "Data visualization validation",
            "Academic publication preparation",
            "Statistical graphics testing"
        ]
    ),
    
    PresetType.MOBILE_APP: Preset(
        name="Mobile App Design",
        description=(
            "Optimized for mobile application design. Uses JPEG with "
            "balanced quality for smaller file sizes, auto-select algorithm "
            "for versatility, and moderate severity for realistic simulation."
        ),
        config=SimulationConfig(
            algorithm=Algorithm.AUTO,
            severity=0.7,
            output_format=OutputFormat.JPEG,
            quality=90,
            optimize=True,
        ),
        recommended_for=[
            "iOS/Android app design",
            "Mobile game UI testing",
            "Responsive design validation",
            "Touch interface accessibility"
        ]
    ),
    
    PresetType.ARCHIVAL: Preset(
        name="Archival",
        description=(
            "Optimized for archival and preservation workflows. Uses "
            "lossless PNG with maximum quality settings and Vischeck algorithm "
            "for compatibility with legacy accessibility standards."
        ),
        config=SimulationConfig(
            algorithm=Algorithm.VISCHECK,
            severity=1.0,
            output_format=OutputFormat.PNG,
            quality=95,
            optimize=True,
        ),
        recommended_for=[
            "Digital preservation projects",
            "Museum digitization",
            "Historical document accessibility",
            "Long-term archival storage"
        ]
    ),
    
    PresetType.FAST_PREVIEW: Preset(
        name="Fast Preview",
        description=(
            "Optimized for quick previews and iterative design. Uses JPEG "
            "with reduced quality for speed, Brettel 1997 for computational "
            "efficiency, and lower severity for faster processing."
        ),
        config=SimulationConfig(
            algorithm=Algorithm.BRETTEL_1997,
            severity=0.6,
            output_format=OutputFormat.JPEG,
            quality=75,
            optimize=True,
        ),
        recommended_for=[
            "Rapid prototyping",
            "Design iteration cycles",
            "Quick accessibility checks",
            "Bulk preview generation"
        ]
    ),
}


def get_preset(preset_type: PresetType | str) -> Preset:
    """Get a preset configuration by type.
    
    Args:
        preset_type: The preset type enum or string name.
    
    Returns:
        Preset configuration with metadata.
    
    Raises:
        ValueError: If preset type is not recognized.
    
    Example:
        >>> from cvd_simulator.presets import get_preset, PresetType
        >>> preset = get_preset(PresetType.WEB_DESIGN)
        >>> print(preset.name)
        'Web Design'
        >>> config = preset.config
    """
    if isinstance(preset_type, str):
        try:
            preset_type = PresetType(preset_type.lower())
        except ValueError:
            available = ", ".join(p.value for p in PresetType)
            raise ValueError(
                f"Unknown preset '{preset_type}'. Available: {available}"
            )
    
    return PRESETS[preset_type]


def list_presets() -> dict[PresetType, Preset]:
    """Get all available presets.
    
    Returns:
        Dictionary mapping preset types to Preset objects.
    """
    return PRESETS.copy()


def apply_preset(
    preset_type: PresetType | str,
    output_directory: Path | None = None
) -> SimulationConfig:
    """Apply a preset and return a SimulationConfig.
    
    Args:
        preset_type: The preset to apply.
        output_directory: Optional override for output directory.
    
    Returns:
        SimulationConfig configured according to the preset.
    """
    import copy
    preset = get_preset(preset_type)
    config = copy.copy(preset.config)
    
    if output_directory is not None:
        config.output_directory = output_directory
    
    return config


def create_custom_preset(
    name: str,
    description: str,
    config: SimulationConfig,
    recommended_for: list[str] | None = None
) -> Preset:
    """Create a custom preset.
    
    Args:
        name: Display name for the preset.
        description: Description of the preset.
        config: SimulationConfig for the preset.
        recommended_for: List of recommended use cases.
    
    Returns:
        Custom Preset instance.
    """
    return Preset(
        name=name,
        description=description,
        config=config,
        recommended_for=recommended_for or []
    )


def preset_to_dict(preset: Preset) -> dict[str, Any]:
    """Convert a preset to a dictionary.
    
    Args:
        preset: Preset to convert.
    
    Returns:
        Dictionary representation of the preset.
    """
    return {
        "name": preset.name,
        "description": preset.description,
        "config": preset.config.to_dict(),
        "recommended_for": preset.recommended_for
    }


def print_preset_info(preset_type: PresetType | str) -> None:
    """Print detailed information about a preset.
    
    Args:
        preset_type: The preset to display information for.
    """
    preset = get_preset(preset_type)
    
    print(f"\n{'=' * 60}")
    print(f"Preset: {preset.name}")
    print(f"{'=' * 60}")
    print(f"\nDescription:\n  {preset.description}\n")
    
    print("Configuration:")
    config_dict = preset.config.to_dict()
    for key, value in config_dict.items():
        print(f"  {key}: {value}")
    
    if preset.recommended_for:
        print("\nRecommended for:")
        for use_case in preset.recommended_for:
            print(f"  • {use_case}")
    
    print()


__all__ = [
    "PresetType",
    "Preset",
    "PRESETS",
    "get_preset",
    "list_presets",
    "apply_preset",
    "create_custom_preset",
    "preset_to_dict",
    "print_preset_info"
]
