"""Main simulator module for the CVD Simulator application.

This module provides the core CVDSimulator class that orchestrates
the simulation of color vision deficiencies using various algorithms.
"""

from __future__ import annotations
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from multiprocessing import cpu_count
from pathlib import Path
from typing import Callable

import numpy as np
from PIL import Image

from cvd_simulator.config import SimulationConfig
from cvd_simulator.core.image_loader import ImageLoader
from cvd_simulator.core.output_writer import OutputWriter
from cvd_simulator.enums import Algorithm, CVDType
from cvd_simulator.exceptions import (
    BatchProcessingError,
    CVDSimulatorError,
)
from cvd_simulator.utils.logging_config import get_logger

logger = get_logger(__name__)


class CVDSimulator:
    """Main simulator class for color vision deficiency simulation.

    This class encapsulates all functionality for simulating color vision
    deficiencies. It coordinates image loading, simulation processing,
    and output writing with support for batch operations.

    Attributes:
        config: SimulationConfig with simulation parameters.
        loader: ImageLoader for loading and validating images.
        writer: OutputWriter for saving processed images.
        _simulator: Internal daltonlens simulator instance.

    Example:
        >>> config = SimulationConfig(algorithm=Algorithm.MACHADO_2009)
        >>> simulator = CVDSimulator(config)
        >>> results = simulator.process_image(Path("input.jpg"))
    """

    def __init__(self, config: SimulationConfig | None = None):
        """Initialize the CVD simulator.

        Args:
            config: Optional SimulationConfig. Uses defaults if not provided.
        """
        self.config = config or SimulationConfig()
        self.loader = ImageLoader()
        self.writer = OutputWriter(self.config)

        # Initialize the daltonlens simulator
        simulator_class = self.config.algorithm.get_simulator_class()
        self._simulator = simulator_class()

        logger.info(
            f"CVDSimulator initialized with algorithm: {self.config.algorithm.name}, "
            f"severity: {self.config.severity}"
        )

    def simulate(self, image: Image.Image, cvd_type: CVDType) -> Image.Image:
        """Apply CVD simulation to an image.

        Simulates how the image appears to individuals with the
        specified color vision deficiency.

        Args:
            image: PIL Image to process (RGB mode).
            cvd_type: Type of color vision deficiency to simulate.

        Returns:
            Simulated PIL Image in RGB mode.

        Raises:
            CVDSimulatorError: If simulation fails.

        Example:
            >>> simulator = CVDSimulator()
            >>> image = Image.new('RGB', (100, 100), color='red')
            >>> result = simulator.simulate(image, CVDType.PROTAN)
        """
        logger.debug(f"Simulating {cvd_type.name}")

        try:
            # Handle grayscale specially
            if cvd_type == CVDType.GRAYSCALE:
                result = image.convert("L").convert("RGB")
                logger.debug("Grayscale conversion complete")
                return result

            # Convert image to numpy array
            image_array = self.loader.to_numpy(image)

            # Get the deficiency enum from daltonlens
            from daltonlens import simulate

            deficiency = getattr(simulate.Deficiency, cvd_type.name)

            # Apply simulation
            result_array = self._simulator.simulate_cvd(
                image_array, deficiency, severity=self.config.severity
            )

            # Convert back to PIL Image
            result = self.loader.from_numpy(result_array)

            logger.debug(f"Simulation complete: {cvd_type.name}")
            return result

        except Exception as e:
            logger.error(f"Simulation failed: {e}")
            raise CVDSimulatorError(f"Failed to simulate {cvd_type.name}: {e}")

    def process_image(
        self, image_path: Path | str, output_timestamp: str | None = None
    ) -> dict[CVDType, Path]:
        """Process an image for all CVD types.

        Loads the image, applies all CVD simulations, and saves
        the results to the configured output directory.

        Args:
            image_path: Path to the input image.
            output_timestamp: Optional timestamp for output filenames.

        Returns:
            Dictionary mapping CVDType to output file paths.

        Raises:
            CVDSimulatorError: If simulation fails.

        Example:
            >>> simulator = CVDSimulator()
            >>> results = simulator.process_image("input.jpg")
            >>> print(results[CVDType.PROTAN])
            outputs/protan_image_20260212_153045.jpg
        """
        # Convert to Path
        if isinstance(image_path, str):
            image_path = Path(image_path)

        logger.info(f"Processing image: {image_path}")

        # Load the image
        image = self.loader.load(image_path)

        # Generate timestamp
        timestamp = output_timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")

        # Process all CVD types
        results: dict[CVDType, Path] = {}

        for cvd_type in CVDType:
            try:
                # Simulate
                simulated = self.simulate(image, cvd_type)

                # Save
                output_path = self.writer.save(simulated, cvd_type, timestamp)
                results[cvd_type] = output_path

                logger.info(f"Processed {cvd_type.name}: {output_path}")

            except Exception as e:
                logger.error(f"Failed to process {cvd_type.name}: {e}")
                raise

        logger.info(f"Image processing complete: {len(results)} outputs")
        return results

    def process_batch(
        self, image_paths: list[Path | str], max_workers: int | None = None
    ) -> dict[Path, dict[CVDType, Path] | None]:
        """Process multiple images in parallel.

        Processes multiple images sequentially but reports progress.
        For true parallelism, consider running multiple CLI instances.

        Args:
            image_paths: List of paths to input images.
            max_workers: Number of parallel workers (reserved for future use).

        Returns:
            Dictionary mapping input paths to result dictionaries.
            Failed images have None as their value.

        Raises:
            BatchProcessingError: If all images fail to process.

        Example:
            >>> simulator = CVDSimulator()
            >>> images = [Path("a.jpg"), Path("b.jpg")]
            >>> results = simulator.process_batch(images)
        """
        if not image_paths:
            logger.warning("No images to process")
            return {}

        workers = max_workers or self.config.max_workers or cpu_count()
        logger.info(f"Batch processing {len(image_paths)} images (workers: {workers})")

        results: dict[Path, dict[CVDType, Path] | None] = {}
        failed: list[Path] = []
        success_count = 0

        for path in image_paths:
            path = Path(path) if isinstance(path, str) else path

            try:
                result = self.process_image(path)
                results[path] = result
                success_count += 1
            except Exception as e:
                logger.error(f"Failed to process {path}: {e}")
                results[path] = None
                failed.append(path)

        # Report results
        if failed:
            logger.warning(f"Batch complete: {success_count} succeeded, {len(failed)} failed")
            if success_count == 0:
                raise BatchProcessingError(
                    "All images failed to process", failed_items=failed, success_count=0
                )
        else:
            logger.info(f"Batch complete: all {success_count} images processed successfully")

        return results

    def get_supported_algorithms(self) -> list[Algorithm]:
        """Get list of supported simulation algorithms.

        Returns:
            List of available Algorithm enum values.
        """
        return list(Algorithm)

    def get_supported_cvd_types(self) -> list[CVDType]:
        """Get list of supported CVD types.

        Returns:
            List of available CVDType enum values.
        """
        return list(CVDType)


def _process_single_image(args: tuple) -> dict[CVDType, Path] | None:
    """Process a single image (used for parallel execution).

    Args:
        args: Tuple of (image_path, config_dict)

    Returns:
        Dictionary mapping CVDType to output paths, or None if failed.
    """
    image_path, config_dict = args
    try:
        config = SimulationConfig.from_dict(config_dict)
        simulator = CVDSimulator(config)
        return simulator.process_image(Path(image_path))
    except Exception as e:
        logger.error(f"Failed to process {image_path} in worker: {e}")
        return None


def _process_single_image_with_type(args: tuple) -> Path | None:
    """Process a single image with specific CVD type (used for parallel execution).

    Args:
        args: Tuple of (image_path, cvd_type_name, config_dict)

    Returns:
        Output path or None if failed.
    """
    image_path, cvd_type_name, config_dict = args
    try:
        config = SimulationConfig.from_dict(config_dict)
        simulator = CVDSimulator(config)
        cvd_type = CVDType[cvd_type_name]

        image = simulator.loader.load(Path(image_path))
        simulated = simulator.simulate(image, cvd_type)
        return simulator.writer.save(simulated, cvd_type)
    except Exception as e:
        logger.error(f"Failed to process {image_path} in worker: {e}")
        return None


class AsyncCVDSimulator(CVDSimulator):
    """Async-capable simulator for high-throughput batch processing.

    This class extends CVDSimulator with parallel processing capabilities
    using ProcessPoolExecutor for CPU-intensive image operations.

    Attributes:
        config: SimulationConfig with simulation parameters.
        max_workers: Maximum number of parallel workers.

    Example:
        >>> config = SimulationConfig(max_workers=4)
        >>> simulator = AsyncCVDSimulator(config)
        >>> results = simulator.process_batch_parallel(image_paths)
    """

    def __init__(self, config: SimulationConfig | None = None, max_workers: int | None = None):
        """Initialize the async CVD simulator.

        Args:
            config: Optional SimulationConfig. Uses defaults if not provided.
            max_workers: Optional override for number of parallel workers.
        """
        super().__init__(config)
        self.max_workers = max_workers or self.config.max_workers or cpu_count()
        logger.info(f"AsyncCVDSimulator initialized with {self.max_workers} workers")

    def process_batch_parallel(
        self,
        image_paths: list[Path | str],
        cvd_type: CVDType | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict[Path, dict[CVDType, Path] | Path | None]:
        """Process multiple images in parallel.

        Uses ProcessPoolExecutor to process images concurrently,
        significantly improving throughput for batch operations.

        Args:
            image_paths: List of paths to input images.
            cvd_type: Optional specific CVD type to simulate. If None,
                all CVD types are processed for each image.
            progress_callback: Optional callback function called with
                (completed_count, total_count) after each image.

        Returns:
            Dictionary mapping input paths to result dictionaries.
            If cvd_type is specified, maps to single Path.
            Failed images have None as their value.

        Raises:
            BatchProcessingError: If all images fail to process.

        Example:
            >>> simulator = AsyncCVDSimulator()
            >>> results = simulator.process_batch_parallel(image_paths)
            >>> for path, result in results.items():
            ...     print(f"{path}: {result}")
        """
        if not image_paths:
            logger.warning("No images to process")
            return {}

        total = len(image_paths)
        logger.info(
            f"Starting parallel batch processing: {total} images, " f"{self.max_workers} workers"
        )

        # Prepare arguments for workers
        config_dict = self.config.to_dict()

        if cvd_type:
            # Process single type for all images
            args_list = [(str(path), cvd_type.name, config_dict) for path in image_paths]
            process_func = _process_single_image_with_type
        else:
            # Process all types for all images
            args_list = [(str(path), config_dict) for path in image_paths]
            process_func = _process_single_image

        results: dict[Path, dict[CVDType, Path] | Path | None] = {}
        failed: list[Path] = []
        success_count = 0
        completed = 0

        with ProcessPoolExecutor(max_workers=self.max_workers) as executor:
            futures = {executor.submit(process_func, args): Path(args[0]) for args in args_list}

            for future in as_completed(futures):
                path = futures[future]
                completed += 1

                try:
                    result = future.result()
                    if result is not None:
                        results[path] = result
                        success_count += 1
                        logger.info(f"Processed {path} ({completed}/{total})")
                    else:
                        results[path] = None
                        failed.append(path)
                        logger.error(f"Failed to process {path}")
                except Exception as e:
                    logger.error(f"Exception processing {path}: {e}")
                    results[path] = None
                    failed.append(path)

                # Call progress callback if provided
                if progress_callback:
                    progress_callback(completed, total)

        # Report results
        if failed:
            logger.warning(f"Batch complete: {success_count} succeeded, {len(failed)} failed")
            if success_count == 0:
                raise BatchProcessingError(
                    "All images failed to process", failed_items=failed, success_count=0
                )
        else:
            logger.info(f"Batch complete: all {success_count} images processed")

        return results

    def process_batch_chunked(
        self, image_paths: list[Path | str], chunk_size: int = 10, cvd_type: CVDType | None = None
    ) -> dict[Path, dict[CVDType, Path] | Path | None]:
        """Process images in chunks to manage memory usage.

        Processes images in smaller batches to prevent memory exhaustion
        with large image sets.

        Args:
            image_paths: List of paths to input images.
            chunk_size: Number of images to process per chunk.
            cvd_type: Optional specific CVD type to simulate.

        Returns:
            Combined dictionary of all results.

        Example:
            >>> simulator = AsyncCVDSimulator()
            >>> # Process 1000 images in chunks of 50
            >>> results = simulator.process_batch_chunked(
            ...     image_paths, chunk_size=50
            ... )
        """
        if not image_paths:
            return {}

        all_results: dict[Path, dict[CVDType, Path] | Path | None] = {}
        total = len(image_paths)
        chunks = [image_paths[i : i + chunk_size] for i in range(0, total, chunk_size)]

        logger.info(f"Processing {total} images in {len(chunks)} chunks " f"(size: {chunk_size})")

        for i, chunk in enumerate(chunks):
            logger.info(f"Processing chunk {i + 1}/{len(chunks)}")
            chunk_results = self.process_batch_parallel(chunk, cvd_type)
            all_results.update(chunk_results)

        return all_results


def get_optimal_workers(image_count: int, image_size_mb: float = 1.0) -> int:
    """Calculate optimal number of workers based on system and workload.

    Args:
        image_count: Number of images to process.
        image_size_mb: Estimated average image size in MB.

    Returns:
        Recommended number of workers.

    Example:
        >>> workers = get_optimal_workers(100, image_size_mb=5.0)
        >>> print(f"Using {workers} workers")
    """
    try:
        import psutil

        available_memory_gb = psutil.virtual_memory().available / (1024**3)
    except ImportError:
        available_memory_gb = 4.0  # Default assumption

    available_cpus = cpu_count()

    # Memory constraint: assume each worker needs ~3x image size
    memory_based_limit = int(available_memory_gb / (image_size_mb * 3 / 1024))

    # Don't exceed CPU count significantly for CPU-bound tasks
    cpu_based_limit = available_cpus

    # Don't create more workers than images
    count_based_limit = image_count

    optimal = min(memory_based_limit, cpu_based_limit, count_based_limit)
    optimal = max(1, optimal)  # At least 1 worker

    return optimal


class CVDSimulatorParallel(AsyncCVDSimulator):
    """Alias for AsyncCVDSimulator for backward compatibility.

    .. deprecated:: 1.1.1
        Use :class:`AsyncCVDSimulator` directly.
    """

    pass


__all__ = ["CVDSimulator", "AsyncCVDSimulator", "CVDSimulatorParallel", "get_optimal_workers"]
