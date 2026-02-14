"""Unit tests for the preset configuration system."""

import pytest
from pathlib import Path

from cvd_simulator.presets import (
    PresetType,
    Preset,
    PRESETS,
    get_preset,
    list_presets,
    apply_preset,
    create_custom_preset,
    preset_to_dict,
)
from cvd_simulator.config import SimulationConfig
from cvd_simulator.enums import Algorithm, OutputFormat


class TestPresetType:
    """Tests for PresetType enum."""

    def test_preset_type_values(self):
        """Test preset type values are correct."""
        assert PresetType.WEB_DESIGN.value == "web_design"
        assert PresetType.PRINT_MEDIA.value == "print_media"
        assert PresetType.SCIENTIFIC_VISUALIZATION.value == "scientific_visualization"
        assert PresetType.MOBILE_APP.value == "mobile_app"
        assert PresetType.ARCHIVAL.value == "archival"
        assert PresetType.FAST_PREVIEW.value == "fast_preview"


class TestGetPreset:
    """Tests for get_preset function."""

    def test_get_preset_by_enum(self):
        """Test getting preset by enum."""
        preset = get_preset(PresetType.WEB_DESIGN)
        assert isinstance(preset, Preset)
        assert preset.name == "Web Design"

    def test_get_preset_by_string(self):
        """Test getting preset by string."""
        preset = get_preset("web_design")
        assert isinstance(preset, Preset)
        assert preset.name == "Web Design"

    def test_get_preset_invalid_string(self):
        """Test error on invalid preset string."""
        with pytest.raises(ValueError, match="Unknown preset"):
            get_preset("invalid_preset")

    def test_all_presets_available(self):
        """Test all preset types have corresponding presets."""
        for preset_type in PresetType:
            preset = get_preset(preset_type)
            assert preset is not None
            assert isinstance(preset.config, SimulationConfig)


class TestWebDesignPreset:
    """Tests for Web Design preset."""

    def test_web_design_config(self):
        """Test Web Design preset configuration."""
        preset = get_preset(PresetType.WEB_DESIGN)
        config = preset.config

        assert config.algorithm == Algorithm.MACHADO_2009
        assert config.severity == 0.8
        assert config.output_format == OutputFormat.WEBP
        assert config.quality == 85
        assert config.optimize is True

    def test_web_design_metadata(self):
        """Test Web Design preset metadata."""
        preset = get_preset(PresetType.WEB_DESIGN)

        assert "Web Design" in preset.name
        assert "web" in preset.description.lower()
        assert len(preset.recommended_for) > 0


class TestPrintMediaPreset:
    """Tests for Print Media preset."""

    def test_print_media_config(self):
        """Test Print Media preset configuration."""
        preset = get_preset(PresetType.PRINT_MEDIA)
        config = preset.config

        assert config.algorithm == Algorithm.VIENOT_1999
        assert config.severity == 1.0
        assert config.output_format == OutputFormat.PNG
        assert config.quality == 95


class TestScientificVisualizationPreset:
    """Tests for Scientific Visualization preset."""

    def test_scientific_config(self):
        """Test Scientific Visualization preset configuration."""
        preset = get_preset(PresetType.SCIENTIFIC_VISUALIZATION)
        config = preset.config

        assert config.algorithm == Algorithm.BRETTEL_1997
        assert config.output_format == OutputFormat.TIFF


class TestApplyPreset:
    """Tests for apply_preset function."""

    def test_apply_preset_default_output(self):
        """Test applying preset with default output directory."""
        config = apply_preset(PresetType.WEB_DESIGN)
        assert isinstance(config, SimulationConfig)
        assert config.algorithm == Algorithm.MACHADO_2009

    def test_apply_preset_custom_output(self):
        """Test applying preset with custom output directory."""
        custom_output = Path("./custom_outputs")
        config = apply_preset(PresetType.WEB_DESIGN, output_directory=custom_output)
        assert config.output_directory == custom_output


class TestListPresets:
    """Tests for list_presets function."""

    def test_list_presets_returns_dict(self):
        """Test list_presets returns a dictionary."""
        presets = list_presets()
        assert isinstance(presets, dict)
        assert len(presets) == len(PresetType)

    def test_list_presets_contains_all_types(self):
        """Test list_presets contains all preset types."""
        presets = list_presets()
        for preset_type in PresetType:
            assert preset_type in presets


class TestCreateCustomPreset:
    """Tests for create_custom_preset function."""

    def test_create_custom_preset(self):
        """Test creating a custom preset."""
        config = SimulationConfig(algorithm=Algorithm.AUTO)
        preset = create_custom_preset(
            name="Custom Preset",
            description="A custom preset for testing",
            config=config,
            recommended_for=["testing", "development"],
        )

        assert preset.name == "Custom Preset"
        assert preset.description == "A custom preset for testing"
        assert preset.config.algorithm == Algorithm.AUTO
        assert preset.recommended_for == ["testing", "development"]


class TestPresetToDict:
    """Tests for preset_to_dict function."""

    def test_preset_to_dict_structure(self):
        """Test preset_to_dict returns correct structure."""
        preset = get_preset(PresetType.WEB_DESIGN)
        data = preset_to_dict(preset)

        assert "name" in data
        assert "description" in data
        assert "config" in data
        assert "recommended_for" in data
        assert isinstance(data["config"], dict)


class TestPresetImmutability:
    """Tests to ensure presets don't share state."""

    def test_preset_configs_are_independent(self):
        """Test that applying preset doesn't modify original."""
        original = get_preset(PresetType.WEB_DESIGN)
        config1 = apply_preset(PresetType.WEB_DESIGN, output_directory=Path("./out1"))
        config2 = apply_preset(PresetType.WEB_DESIGN, output_directory=Path("./out2"))

        assert config1.output_directory != config2.output_directory
        # Original preset should be unchanged
        assert original.config.output_directory.name == "outputs"
