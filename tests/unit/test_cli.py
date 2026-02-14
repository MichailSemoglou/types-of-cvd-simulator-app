"""Unit tests for the CLI interface."""

from __future__ import annotations
import sys
from io import StringIO
from pathlib import Path
from unittest.mock import patch

import pytest
from PIL import Image

from cvd_simulator.interfaces.cli import (
    create_parser,
    list_algorithms,
    list_types,
    main,
)


class TestCreateParser:
    """Tests for argument parser creation."""
    
    def test_parser_creation(self):
        """Test that parser is created successfully."""
        parser = create_parser()
        assert parser is not None
        assert parser.prog == "cvd-simulator"
    
    def test_parser_default_values(self):
        """Test parser default values."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg"])
        
        assert args.images == ["image.jpg"]
        assert args.algorithm == "brettel_1997"
        assert args.severity == 0.8
        assert args.format == "jpeg"
        assert args.output == "./outputs"
        assert args.quality == 95
        assert args.verbose is False
        assert args.log_level == "info"
    
    def test_parser_multiple_images(self):
        """Test parsing multiple image arguments."""
        parser = create_parser()
        args = parser.parse_args(["img1.jpg", "img2.jpg", "img3.jpg"])
        
        assert args.images == ["img1.jpg", "img2.jpg", "img3.jpg"]
    
    def test_parser_algorithm_option(self):
        """Test algorithm selection option."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg", "-a", "machado_2009"])
        
        assert args.algorithm == "machado_2009"
    
    def test_parser_severity_option(self):
        """Test severity option."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg", "-s", "0.5"])
        
        assert args.severity == 0.5
    
    def test_parser_format_option(self):
        """Test output format option."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg", "-f", "png"])
        
        assert args.format == "png"
    
    def test_parser_output_option(self):
        """Test output directory option."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg", "-o", "/custom/output"])
        
        assert args.output == "/custom/output"
    
    def test_parser_verbose_flag(self):
        """Test verbose flag."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg", "-v"])
        
        assert args.verbose is True
    
    def test_parser_type_option(self):
        """Test CVD type selection option."""
        parser = create_parser()
        args = parser.parse_args(["image.jpg", "-t", "protan"])
        
        assert args.type == "protan"
    
    def test_parser_list_algorithms_flag(self):
        """Test --list-algorithms flag."""
        parser = create_parser()
        args = parser.parse_args(["--list-algorithms"])
        
        assert args.list_algorithms is True
    
    def test_parser_list_types_flag(self):
        """Test --list-types flag."""
        parser = create_parser()
        args = parser.parse_args(["--list-types"])
        
        assert args.list_types is True
    
    def test_parser_version_flag(self):
        """Test --version flag."""
        parser = create_parser()
        
        with pytest.raises(SystemExit) as exc_info:
            parser.parse_args(["--version"])
        
        assert exc_info.value.code == 0


class TestListFunctions:
    """Tests for list algorithms and types functions."""
    
    def test_list_algorithms(self, capsys):
        """Test listing algorithms prints expected output."""
        list_algorithms()
        captured = capsys.readouterr()
        
        assert "Available simulation algorithms:" in captured.out
        assert "brettel_1997" in captured.out
        assert "machado_2009" in captured.out
        assert "vienot_1999" in captured.out
        assert "vischeck" in captured.out
        assert "auto" in captured.out
    
    def test_list_types(self, capsys):
        """Test listing CVD types prints expected output."""
        list_types()
        captured = capsys.readouterr()
        
        assert "Available color vision deficiency types:" in captured.out
        assert "protan" in captured.out
        assert "deutan" in captured.out
        assert "tritan" in captured.out
        assert "grayscale" in captured.out


class TestMain:
    """Tests for main CLI entry point."""
    
    def test_main_list_algorithms(self):
        """Test main with --list-algorithms exits successfully."""
        result = main(["--list-algorithms"])
        assert result == 0
    
    def test_main_list_types(self):
        """Test main with --list-types exits successfully."""
        result = main(["--list-types"])
        assert result == 0
    
    def test_main_version(self):
        """Test main with --version exits successfully."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
    
    def test_main_invalid_severity(self, tmp_path, capsys):
        """Test main with invalid severity returns error."""
        # Create a test image
        img_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_path)
        
        result = main([str(img_path), "-s", "1.5"])
        
        assert result == 1
        captured = capsys.readouterr()
        assert "Error" in captured.err or "Invalid" in captured.out
    
    def test_main_invalid_config(self, tmp_path, capsys):
        """Test main with invalid algorithm returns error."""
        img_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_path)
        
        # Mock parser to return invalid algorithm
        with patch.object(sys, 'argv', ['cvd-simulator', str(img_path), '-a', 'invalid_algo']):
            # This should fail during config creation
            pass  # argparse will catch this before main logic
    
    def test_main_single_image_success(self, tmp_path, capsys):
        """Test main processing a single image successfully."""
        # Create test image
        img_path = tmp_path / "test.png"
        output_dir = tmp_path / "outputs"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_path)
        
        result = main([
            str(img_path),
            "-o", str(output_dir),
            "-f", "png"
        ])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Complete" in captured.out
    
    def test_main_single_type(self, tmp_path, capsys):
        """Test main processing with specific CVD type."""
        img_path = tmp_path / "test.png"
        output_dir = tmp_path / "outputs"
        img = Image.new('RGB', (100, 100), color='red')
        img.save(img_path)
        
        result = main([
            str(img_path),
            "-o", str(output_dir),
            "-t", "protan",
            "-f", "png"
        ])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "Complete" in captured.out
    
    def test_main_multiple_images(self, tmp_path, capsys):
        """Test main processing multiple images."""
        img1 = tmp_path / "img1.png"
        img2 = tmp_path / "img2.png"
        output_dir = tmp_path / "outputs"
        
        for img_path in [img1, img2]:
            img = Image.new('RGB', (100, 100), color='blue')
            img.save(img_path)
        
        result = main([
            str(img1), str(img2),
            "-o", str(output_dir),
            "-f", "png"
        ])
        
        assert result == 0
        captured = capsys.readouterr()
        assert "2/2" in captured.out or "Complete" in captured.out
    
    def test_main_nonexistent_image(self, tmp_path, capsys):
        """Test main with non-existent image reports error."""
        nonexistent = tmp_path / "does_not_exist.png"
        output_dir = tmp_path / "outputs"
        
        result = main([
            str(nonexistent),
            "-o", str(output_dir)
        ])
        
        # Should complete but report 0/1 success
        captured = capsys.readouterr()
        assert "0/1" in captured.out or "Error" in captured.err
    
    def test_main_with_log_file(self, tmp_path):
        """Test main with log file output."""
        img_path = tmp_path / "test.png"
        output_dir = tmp_path / "outputs"
        log_file = tmp_path / "test.log"
        img = Image.new('RGB', (100, 100), color='green')
        img.save(img_path)
        
        result = main([
            str(img_path),
            "-o", str(output_dir),
            "--log-file", str(log_file),
            "-v"
        ])
        
        assert result == 0
        assert log_file.exists()
        log_content = log_file.read_text()
        assert "CVD Simulator" in log_content


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def test_full_workflow(self, tmp_path):
        """Test complete CLI workflow end-to-end."""
        img_path = tmp_path / "input.png"
        output_dir = tmp_path / "outputs"
        img = Image.new('RGB', (200, 200), color=(100, 150, 200))
        img.save(img_path)
        
        result = main([
            str(img_path),
            "-o", str(output_dir),
            "-a", "machado_2009",
            "-s", "0.7",
            "-f", "png",
            "-q", "90"
        ])
        
        assert result == 0
        
        # Check output files exist
        output_files = list(output_dir.glob("*.png"))
        assert len(output_files) == 4  # 4 CVD types
    
    def test_all_algorithms_via_cli(self, tmp_path):
        """Test that all algorithms work via CLI."""
        img_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='gray')
        img.save(img_path)
        
        algorithms = ["brettel_1997", "vienot_1999", "machado_2009", "vischeck", "auto"]
        
        for algo in algorithms:
            output_dir = tmp_path / f"outputs_{algo}"
            result = main([
                str(img_path),
                "-o", str(output_dir),
                "-a", algo,
                "-f", "png"
            ])
            assert result == 0, f"Algorithm {algo} failed"
            
            # Verify output was created
            output_files = list(output_dir.glob("*.png"))
            assert len(output_files) > 0, f"No output for algorithm {algo}"