# CVD Simulator

A comprehensive Python package for simulating color vision deficiencies (CVD), including protanopia, deuteranopia, and tritanopia. This tool uses scientifically-validated algorithms to simulate how images appear to individuals with different types of color blindness.

## Features

- **Multiple Simulation Algorithms**: Support for Brettel (1997), Viénot (1999), Machado (2009), Vischeck, and Auto-select algorithms
- **All CVD Types**: Simulate protanopia, deuteranopia, tritanopia, and grayscale (achromatopsia)
- **Batch Processing**: Process multiple images efficiently with progress bars
- **Configuration Presets**: Quick presets for Web Design, Print Media, Scientific Visualization, and more
- **Video Frame Extraction**: Basic video processing with FFmpeg integration
- **Metadata Export**: JSON sidecar files for reproducibility
- **Performance Profiling**: Built-in timing and performance analysis
- **Flexible Configuration**: Configure via code, environment variables, CLI arguments, or presets
- **Security**: Built-in input validation and path sanitization
- **Type Hints**: Fully typed codebase for better IDE support
- **Comprehensive Testing**: Unit and integration test suite

## Installation

### From PyPI (Recommended)

```bash
pip install cvd-simulator
```

### From Source

```bash
git clone https://github.com/MichailSemoglou/types-of-cvd-simulator-app.git
cd types-of-cvd-simulator-app
pip install -e .
```

### Video Processing (Optional)

For video frame extraction capabilities:

```bash
# macOS
brew install ffmpeg

# Ubuntu/Debian
sudo apt-get install ffmpeg

# Windows (via Chocolatey)
choco install ffmpeg
```

### Development Installation

```bash
pip install -e ".[dev]"
```

## Quick Start

### Command Line Interface

```bash
# Process a single image
cvd-simulator input.jpg

# Process with specific algorithm and severity
cvd-simulator input.jpg -a MACHADO_2009 -s 0.7

# Process multiple images
cvd-simulator img1.jpg img2.jpg img3.jpg

# Output as PNG with custom directory
cvd-simulator input.jpg -f PNG -o ./my_outputs

# List available algorithms
cvd-simulator --list-algorithms

# List available CVD types
cvd-simulator --list-types

# Use a preset configuration (v1.1.1+)
cvd-simulator input.jpg --preset web_design

# Show progress bar during batch processing (v1.1.1+)
cvd-simulator img1.jpg img2.jpg img3.jpg --progress

# Export metadata for reproducibility (v1.1.1+)
cvd-simulator input.jpg --export-metadata

# Enable performance profiling (v1.1.1+)
cvd-simulator input.jpg --profile

# List available presets (v1.1.1+)
cvd-simulator --list-presets
```

### Python API

```python
from pathlib import Path
from cvd_simulator import CVDSimulator, SimulationConfig
from cvd_simulator.enums import Algorithm, CVDType, OutputFormat

# Create configuration
config = SimulationConfig(
    algorithm=Algorithm.MACHADO_2009,
    severity=0.8,
    output_format=OutputFormat.PNG,
    output_directory=Path("./outputs"),
)

# Initialize simulator
simulator = CVDSimulator(config)

# Process a single image
results = simulator.process_image(Path("input.jpg"))

# Access specific CVD simulation
protan_path = results[CVDType.PROTAN]
deutan_path = results[CVDType.DEUTAN]
tritan_path = results[CVDType.TRITAN]
bw_path = results[CVDType.GRAYSCALE]

# Process specific CVD type only
image = simulator.loader.load(Path("input.jpg"))
simulated = simulator.simulate(image, CVDType.PROTAN)

# Batch processing
image_paths = [Path("img1.jpg"), Path("img2.jpg")]
batch_results = simulator.process_batch(image_paths)

# Using configuration presets (v1.1.1+)
from cvd_simulator.presets import apply_preset, PresetType

config = apply_preset(PresetType.WEB_DESIGN)
simulator = CVDSimulator(config)

# Export metadata for reproducibility (v1.1.1+)
from cvd_simulator.utils.metadata import create_metadata, export_metadata, generate_sidecar_path

results = simulator.process_image(Path("input.jpg"))
metadata = create_metadata(
    Path("input.jpg"),
    results,
    config,
    notes="Research batch 2026-02"
)
sidecar_path = generate_sidecar_path("input.jpg")
export_metadata(metadata, sidecar_path)

# Performance profiling (v1.1.1+)
from cvd_simulator.utils.profiling import PerformanceProfiler

profiler = PerformanceProfiler()
with profiler.time_operation("batch_process"):
    results = simulator.process_batch(image_paths)

print(profiler.get_summary())
```

### Configuration via Environment Variables

```bash
export CVD_SIMULATOR_ALGORITHM=MACHADO_2009
export CVD_SIMULATOR_SEVERITY=0.7
export CVD_SIMULATOR_OUTPUT_FORMAT=PNG
export CVD_SIMULATOR_OUTPUT_DIRECTORY=./my_outputs

cvd-simulator input.jpg
```

## Project Structure

```
cvd-simulator/
├── src/
│   ├── cvd_simulator/
│   │   ├── __init__.py
│   │   ├── exceptions.py      # Custom exceptions
│   │   ├── enums.py           # Enumerations (CVDType, Algorithm, etc.)
│   │   ├── config.py          # Configuration management
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── simulator.py   # Main CVDSimulator class
│   │   │   ├── image_loader.py
│   │   │   └── output_writer.py
│   │   ├── interfaces/
│   │   │   ├── __init__.py
│   │   │   └── cli.py         # Command-line interface
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py  # Security validation
│   │       └── logging_config.py
│   └── main.py
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docs/
├── examples/
├── outputs/                   # Default output directory
├── requirements.txt
├── setup.py
├── pyproject.toml
└── README.md
```

## Algorithms

The simulator supports multiple scientifically-validated algorithms:

| Algorithm          | Description                                               |
| ------------------ | --------------------------------------------------------- |
| **Brettel (1997)** | Classic algorithm, widely used, computationally efficient |
| **Viénot (1999)**  | Improved accuracy for severe deficiencies                 |
| **Machado (2009)** | Modern approach, handles severity levels well             |
| **Vischeck**       | Based on the popular Vischeck tool                        |
| **Auto-select**    | Automatically chooses the best algorithm                  |

## CVD Types

| Type          | Description                                         |
| ------------- | --------------------------------------------------- |
| **Protan**    | Protanopia - missing or defective L-cones (red)     |
| **Deutan**    | Deuteranopia - missing or defective M-cones (green) |
| **Tritan**    | Tritanopia - missing or defective S-cones (blue)    |
| **Grayscale** | Achromatopsia - complete color blindness            |

## Testing

Run the test suite:

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=cvd_simulator

# Run only unit tests
pytest tests/unit

# Run only integration tests
pytest tests/integration

# Run with verbose output
pytest -v
```

## Development

### Code Formatting

```bash
# Format with black
black src tests

# Type checking
mypy src

# Linting
flake8 src tests
```

### Building Documentation

```bash
cd docs
make html
```

## References

- Brettel, H., Viénot, F., & Mollon, J. D. (1997). Computerized simulation of color appearance for dichromats. _Journal of the Optical Society of America A_, _14_(10), 2647–2655. https://doi.org/10.1364/JOSAA.14.002647
- Viénot, F., Brettel, H., & Mollon, J. D. (1999). Digital video colourmaps for checking the legibility of displays by dichromats. _Color Research & Application_, _24_(4), 243–252. https://doi.org/10.1002/(SICI)1520-6378(199908)24:4<243::AID-COL5>3.0.CO;2-3
- Machado, G. M., Oliveira, M. M., & Fernandes, L. A. F. (2009). A physiologically-based model for simulation of color vision deficiency. _IEEE Transactions on Visualization and Computer Graphics_, _15_(6), 1291–1298. https://doi.org/10.1109/TVCG.2009.113

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Citation

If you use CVD Simulator in your research, please cite:

```bibtex
@software{semoglou2026cvd,
  author = {Semoglou, Michail},
  title = {CVD Simulator: A Scientifically-Validated Tool for Color Vision Deficiency Simulation},
  year = {2026},
  version = {1.1.1},
  url = {https://github.com/MichailSemoglou/types-of-cvd-simulator-app},
  doi = {10.5281/zenodo.XXXXXX}
}
```

See [CITATION.cff](CITATION.cff) for additional citation formats.

## Acknowledgments

- [DaltonLens](https://github.com/DaltonLens) library for the core simulation algorithms
- [Pillow](https://python-pillow.org/) for image processing
- [NumPy](https://numpy.org/) for numerical operations
