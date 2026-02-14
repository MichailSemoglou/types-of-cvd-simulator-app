Changelog
=========

[1.1.1] - 2026-02-13
--------------------

Added
~~~~~

* Video frame extraction module with FFmpeg integration
* Progress indicators (tqdm) for batch operations
* Configuration presets (Web Design, Print Media, Scientific Visualization, Mobile App, Archival, Fast Preview)
* JSON metadata export sidecar files for reproducibility
* Performance profiling and timing utilities
* CITATION.cff for DOI and academic citation
* PyPI publishing workflow via GitHub Actions

Features
~~~~~~~~

* ``--preset`` CLI flag for quick configuration selection
* ``--progress`` CLI flag for progress bars during batch processing
* ``--export-metadata`` CLI flag for reproducible research
* ``--profile`` CLI flag for performance analysis
* ``VideoProcessor`` class for video frame extraction
* ``PerformanceProfiler`` for timing operations
* ``SimulationMetadata`` for capturing simulation context

Documentation
~~~~~~~~~~~~~

* Added CITATION.cff for Zenodo DOI integration
* Updated CLI documentation with new flags
* Added preset configuration documentation

[1.0.0] - 2024-02-13
--------------------

Added
~~~~~

* Initial release of CVD Simulator
* Support for 5 simulation algorithms (Brettel 1997, Viénot 1999, Machado 2009, Vischeck, Auto)
* Support for 4 CVD types (Protan, Deutan, Tritan, Grayscale)
* Command-line interface with comprehensive options
* Python API with full type hints
* Batch processing with sequential and parallel execution
* Flexible configuration (code, environment variables, CLI)
* Security validation (path sanitization, file size limits, format whitelisting)
* Comprehensive test suite (unit, integration, property-based, benchmarks)
* Full documentation with Sphinx
* CI/CD pipeline with GitHub Actions
* Docker support
* Pydantic integration for configuration validation

Features
~~~~~~~~

* Multi-algorithm CVD simulation
* Batch image processing
* Parallel processing with ProcessPoolExecutor
* Configurable output formats (JPEG, PNG, WebP, TIFF, BMP)
* Progress callbacks for batch operations
* Logging with colored output
* Custom exception hierarchy
* Security validators for safe file handling

Documentation
~~~~~~~~~~~~~

* User guide with installation and usage instructions
* API reference with auto-generated documentation
* Algorithm explanations with scientific references
* Contributing guidelines
* Architecture diagrams

Testing
~~~~~~~

* Unit tests for all modules
* Integration tests for end-to-end workflows
* Property-based tests with Hypothesis
* Performance benchmarks with pytest-benchmark
* CLI tests for command-line interface
* 80%+ code coverage
