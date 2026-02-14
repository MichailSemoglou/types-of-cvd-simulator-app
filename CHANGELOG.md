# Changelog

All notable changes to the **CVD Simulator** project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [1.1.1] — 2026-02-13

### New Features

- **Multiple Simulation Algorithms** — Support for Brettel (1997), Viénot (1999), Machado (2009), Vischeck, and an auto-select mode that picks the best algorithm for the requested CVD type.
- **All CVD Types** — Simulate protanopia, deuteranopia, tritanopia, and achromatopsia (full grayscale) with adjustable severity from 0.0 to 1.0.
- **Batch Processing** — Process multiple images in a single invocation with `tqdm` progress bars and `rich` console output.
- **Configuration Presets** — Built-in presets for common workflows: Web Design, Print Media, Scientific Visualization, and more (`PresetType` enum / `apply_preset()`).
- **Video Frame Extraction** — Basic video processing via FFmpeg integration (`VideoProcessor`).
- **Metadata Export** — JSON sidecar files recording algorithm, severity, CVD type, and timing for full reproducibility (`SimulationMetadata`, `export_metadata()`).
- **Performance Profiling** — Built-in `PerformanceProfiler` and `Timer` utilities for benchmarking simulation pipelines.
- **Flexible Configuration** — Configure via Python API (`SimulationConfig`), environment variables, CLI arguments, or presets. Optional Pydantic model available (`SimulationConfigPydantic`).
- **Async Support** — `AsyncCVDSimulator` for non-blocking batch processing in asynchronous applications.
- **Security & Validation** — Input validation, path sanitization, and file-size limits to harden against malicious inputs (`validators` module).
- **Type Safety** — Fully typed codebase with `mypy --strict` compliance; custom exception hierarchy (`CVDSimulatorError`, `ImageProcessingError`, `SecurityError`, `ValidationError`, `ConfigurationError`).
- **CLI** — Feature-rich command-line interface (`cvd-simulator`) with support for `--list-algorithms`, `--list-cvd-types`, format selection, output directories, and more.
- **Comprehensive Test Suite** — Unit, integration, property-based (Hypothesis), and benchmark (pytest-benchmark) tests with coverage reporting.
- **Documentation** — Sphinx-based docs (RST) with autodoc, type hints, and Read the Docs–compatible configuration.
- **Docker Support** — `Dockerfile` and `docker-compose.yml` for containerised usage.
- **CI/CD** — GitHub Actions workflow for automated PyPI publishing on release.

### Known Issues

- Zenodo DOIs are placeholders (`10.5281/zenodo.XXXXXXX`) — they will be minted automatically after the first GitHub release with the Zenodo integration enabled.
- Video processing requires a system-installed FFmpeg binary; it is not bundled with the package.

---

## [Unreleased]

_No unreleased changes._

---

[1.1.1]: https://github.com/MichailSemoglou/types-of-cvd-simulator-app/releases/tag/v1.1.1
[Unreleased]: https://github.com/MichailSemoglou/types-of-cvd-simulator-app/compare/v1.1.1...HEAD
