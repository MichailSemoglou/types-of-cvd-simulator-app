"""Command-line interface for the CVD Simulator application.

This module provides a CLI using argparse for processing images
with CVD simulation from the command line.
"""

from __future__ import annotations
import argparse
import sys
import time
from pathlib import Path
from typing import Sequence

try:
    from tqdm import tqdm
    TQDM_AVAILABLE = True
except ImportError:
    TQDM_AVAILABLE = False

try:
    from rich.console import Console
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from cvd_simulator import CVDSimulator, SimulationConfig, __version__
from cvd_simulator.enums import Algorithm, CVDType, LogLevel, OutputFormat
from cvd_simulator.exceptions import CVDSimulatorError
from cvd_simulator.utils.logging_config import setup_logging
from cvd_simulator.utils.metadata import create_metadata, export_metadata, generate_sidecar_path
from cvd_simulator.utils.profiling import PerformanceProfiler, get_global_profiler
from cvd_simulator.presets import PresetType, get_preset, list_presets, print_preset_info


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI.
    
    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="cvd-simulator",
        description="Simulate color vision deficiencies in images.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Process a single image
  cvd-simulator input.jpg
  
  # Process with specific algorithm and severity
  cvd-simulator input.jpg -a machado_2009 -s 0.7
  
  # Process multiple images with progress bar
  cvd-simulator img1.jpg img2.jpg img3.jpg --progress
  
  # Use a preset configuration
  cvd-simulator input.jpg --preset web_design
  
  # Output as PNG with custom directory
  cvd-simulator input.jpg -f PNG -o ./my_outputs
  
  # Export metadata for reproducibility
  cvd-simulator input.jpg --export-metadata
  
  # Show performance profile
  cvd-simulator input.jpg --profile
  
  # Enable verbose logging
  cvd-simulator input.jpg -v
        """
    )
    
    # Positional arguments
    parser.add_argument(
        "images",
        nargs="*",
        type=str,
        help="Path(s) to input image(s)"
    )
    
    # Algorithm selection
    parser.add_argument(
        "-a", "--algorithm",
        type=str.lower,
        choices=[a.name.lower() for a in Algorithm],
        default="brettel_1997",
        help="Simulation algorithm (default: brettel_1997)"
    )
    
    # Severity
    parser.add_argument(
        "-s", "--severity",
        type=float,
        default=0.8,
        help="Severity of deficiency 0.0-1.0 (default: 0.8)"
    )
    
    # Output format
    parser.add_argument(
        "-f", "--format",
        type=str,
        choices=[f.name.lower() for f in OutputFormat],
        default="jpeg",
        help="Output image format (default: jpeg)"
    )
    
    # Output directory
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="./outputs",
        help="Output directory (default: ./outputs)"
    )
    
    # Quality
    parser.add_argument(
        "-q", "--quality",
        type=int,
        default=95,
        help="JPEG/WebP quality 1-95 (default: 95)"
    )
    
    # Logging
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Enable verbose (debug) logging"
    )
    
    parser.add_argument(
        "--log-level",
        type=str,
        choices=[l.name.lower() for l in LogLevel],
        default="info",
        help="Logging level (default: info)"
    )
    
    parser.add_argument(
        "--log-file",
        type=str,
        help="Optional log file path"
    )
    
    # CVD type selection (optional - process all if not specified)
    parser.add_argument(
        "-t", "--type",
        type=str,
        choices=[t.name.lower() for t in CVDType],
        help="Specific CVD type to simulate (default: all types)"
    )
    
    # Progress bar
    parser.add_argument(
        "--progress",
        action="store_true",
        help="Show progress bar during processing"
    )
    
    # Preset configuration
    parser.add_argument(
        "--preset",
        type=str,
        choices=[p.value for p in PresetType],
        help="Use a preset configuration (web_design, print_media, scientific_visualization, etc.)"
    )
    
    parser.add_argument(
        "--list-presets",
        action="store_true",
        help="List available presets and exit"
    )
    
    # Metadata export
    parser.add_argument(
        "--export-metadata",
        action="store_true",
        help="Export JSON metadata sidecar files for reproducibility"
    )
    
    # Performance profiling
    parser.add_argument(
        "--profile",
        action="store_true",
        help="Enable performance profiling and print summary"
    )
    
    # Video processing (placeholder for v1.1.1)
    parser.add_argument(
        "--video",
        action="store_true",
        help="Process video file (requires FFmpeg)"
    )
    
    parser.add_argument(
        "--video-fps",
        type=float,
        default=None,
        help="Frames per second to extract from video"
    )
    
    # List options
    parser.add_argument(
        "--list-algorithms",
        action="store_true",
        help="List available algorithms and exit"
    )
    
    parser.add_argument(
        "--list-types",
        action="store_true",
        help="List available CVD types and exit"
    )
    
    # Version
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}"
    )
    
    return parser


def list_algorithms() -> None:
    """Print available algorithms."""
    print("Available simulation algorithms:")
    print()
    descriptions = {
        Algorithm.BRETTEL_1997: "Brettel et al. 1997 - Classic algorithm, computationally efficient",
        Algorithm.VIENOT_1999: "Viénot et al. 1999 - Improved accuracy for severe deficiencies",
        Algorithm.MACHADO_2009: "Machado et al. 2009 - Modern, handles severity levels well",
        Algorithm.VISCHECK: "Vischeck - Based on the popular Vischeck tool",
        Algorithm.AUTO: "Auto-select - Automatically chooses best algorithm",
    }
    for algo in Algorithm:
        desc = descriptions.get(algo, "No description available")
        print(f"  {algo.name.lower():15} - {desc}")


def list_types() -> None:
    """Print available CVD types."""
    print("Available color vision deficiency types:")
    print()
    descriptions = {
        CVDType.PROTAN: "Protanopia - Missing or defective L-cones (red)",
        CVDType.DEUTAN: "Deuteranopia - Missing or defective M-cones (green)",
        CVDType.TRITAN: "Tritanopia - Missing or defective S-cones (blue)",
        CVDType.GRAYSCALE: "Achromatopsia - Complete color blindness",
    }
    for cvd_type in CVDType:
        desc = descriptions.get(cvd_type, "No description available")
        print(f"  {cvd_type.name.lower():12} - {desc}")


def list_presets_cli() -> None:
    """Print available presets."""
    print("Available configuration presets:")
    print()
    presets = list_presets()
    for preset_type, preset in presets.items():
        print(f"  {preset_type.value:25} - {preset.name}")
        print(f"      {preset.description[:60]}...")
        print()


def process_single_image(
    image_path: Path,
    simulator: CVDSimulator,
    cvd_type: CVDType | None,
    export_metadata_flag: bool,
    profiler: PerformanceProfiler
) -> tuple[int, dict | None]:
    """Process a single image.
    
    Returns:
        Tuple of (success_count, results_dict or None)
    """
    start_time = time.perf_counter()
    
    try:
        if cvd_type:
            # Process only specific type
            with profiler.time_operation("load_image"):
                image = simulator.loader.load(image_path)
            
            with profiler.time_operation("simulate"):
                simulated = simulator.simulate(image, cvd_type)
            
            with profiler.time_operation("save_output"):
                output_path = simulator.writer.save(simulated, cvd_type)
            
            print(f"  -> {output_path}")
            results = {cvd_type: output_path}
        else:
            # Process all types
            results = simulator.process_image(image_path)
            for cvd_type_key, output_path in results.items():
                print(f"  {cvd_type_key.name:12} -> {output_path}")
        
        # Export metadata if requested
        if export_metadata_flag:
            execution_time = (time.perf_counter() - start_time) * 1000
            metadata = create_metadata(
                image_path,
                results,
                simulator.config,
                execution_time_ms=execution_time
            )
            sidecar_path = generate_sidecar_path(image_path)
            export_metadata(metadata, sidecar_path)
            print(f"  Metadata: {sidecar_path}")
        
        return 1, results
        
    except CVDSimulatorError as e:
        print(f"Error processing {image_path}: {e}", file=sys.stderr)
        return 0, None
    except Exception as e:
        print(f"Unexpected error processing {image_path}: {e}", file=sys.stderr)
        return 0, None


def main(args: Sequence[str] | None = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        args: Command-line arguments. Uses sys.argv if not provided.
    
    Returns:
        Exit code (0 for success, non-zero for errors).
    """
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    # Handle list options
    if parsed.list_algorithms:
        list_algorithms()
        return 0
    
    if parsed.list_types:
        list_types()
        return 0
    
    if parsed.list_presets:
        list_presets_cli()
        return 0
    
    # Validate images are provided for processing
    if not parsed.images:
        parser.error("the following arguments are required: images")
    
    # Setup logging
    log_level = LogLevel.DEBUG if parsed.verbose else LogLevel[parsed.log_level.upper()]
    log_file = Path(parsed.log_file) if parsed.log_file else None
    logger = setup_logging(level=log_level, log_file=log_file)
    
    logger.info(f"CVD Simulator v{__version__} starting")
    
    # Initialize profiler
    profiler = get_global_profiler()
    if not parsed.profile:
        profiler.disable()
    
    # Build configuration
    try:
        if parsed.preset:
            preset = get_preset(parsed.preset)
            config = preset.config
            config.output_directory = Path(parsed.output)
            print(f"Using preset: {preset.name}")
        else:
            config = SimulationConfig(
                algorithm=Algorithm[parsed.algorithm.upper()],
                severity=parsed.severity,
                output_format=OutputFormat[parsed.format.upper()],
                output_directory=Path(parsed.output),
                quality=parsed.quality,
                log_level=log_level,
            )
        logger.debug(f"Configuration: {config.to_dict()}")
    except Exception as e:
        logger.error(f"Invalid configuration: {e}")
        print(f"Error: {e}", file=sys.stderr)
        return 1
    
    # Create simulator
    try:
        simulator = CVDSimulator(config)
    except Exception as e:
        logger.error(f"Failed to initialize simulator: {e}")
        print(f"Error: Failed to initialize simulator: {e}", file=sys.stderr)
        return 1
    
    # Process images
    image_paths = [Path(p) for p in parsed.images]
    success_count = 0
    
    # Determine processing method based on options
    use_progress = parsed.progress and TQDM_AVAILABLE and len(image_paths) > 1
    cvd_type = CVDType[parsed.type.upper()] if parsed.type else None
    
    if use_progress:
        # Use progress bar
        print(f"\nProcessing {len(image_paths)} images...")
        for image_path in tqdm(image_paths, desc="Images", unit="img"):
            print(f"\nProcessing: {image_path}")
            count, _ = process_single_image(
                image_path, simulator, cvd_type,
                parsed.export_metadata, profiler
            )
            success_count += count
    else:
        # Standard processing
        for image_path in image_paths:
            print(f"\nProcessing: {image_path}")
            count, _ = process_single_image(
                image_path, simulator, cvd_type,
                parsed.export_metadata, profiler
            )
            success_count += count
    
    # Summary
    total = len(image_paths)
    logger.info(f"Complete: {success_count}/{total} images processed")
    print(f"\nComplete: {success_count}/{total} images processed successfully")
    
    # Print profile summary if requested
    if parsed.profile:
        print("\n" + profiler.get_summary())
    
    return 0 if success_count == total else 1


if __name__ == "__main__":
    sys.exit(main())
