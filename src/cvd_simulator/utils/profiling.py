"""Performance profiling and timing utilities.

This module provides timing and profiling capabilities for CVD simulation operations,
enabling performance awareness and optimization identification.
"""

from __future__ import annotations

import functools
import time
from collections import defaultdict
from contextlib import contextmanager
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Callable

from cvd_simulator.utils.logging_config import get_logger

if TYPE_CHECKING:
    from pathlib import Path

logger = get_logger(__name__)


@dataclass
class TimingReport:
    """Report of timing measurements.

    Attributes:
        operation: Name of the operation.
        total_time_ms: Total time in milliseconds.
        call_count: Number of calls.
        avg_time_ms: Average time per call in milliseconds.
        min_time_ms: Minimum time in milliseconds.
        max_time_ms: Maximum time in milliseconds.
    """

    operation: str
    total_time_ms: float = 0.0
    call_count: int = 0
    min_time_ms: float = float("inf")
    max_time_ms: float = 0.0

    @property
    def avg_time_ms(self) -> float:
        """Calculate average time per call."""
        if self.call_count == 0:
            return 0.0
        return self.total_time_ms / self.call_count

    def add_measurement(self, time_ms: float) -> None:
        """Add a new timing measurement."""
        self.total_time_ms += time_ms
        self.call_count += 1
        self.min_time_ms = min(self.min_time_ms, time_ms)
        self.max_time_ms = max(self.max_time_ms, time_ms)

    def to_dict(self) -> dict:
        """Convert to dictionary."""
        return {
            "operation": self.operation,
            "total_time_ms": round(self.total_time_ms, 2),
            "call_count": self.call_count,
            "avg_time_ms": round(self.avg_time_ms, 2),
            "min_time_ms": round(self.min_time_ms, 2) if self.call_count > 0 else 0,
            "max_time_ms": round(self.max_time_ms, 2),
        }


class PerformanceProfiler:
    """Profiler for tracking performance metrics.

    This class provides a centralized way to track timing across
    multiple operations in the CVD simulator.

    Example:
        >>> profiler = PerformanceProfiler()
        >>> with profiler.time_operation("image_load"):
        ...     image = load_image(path)
        >>> with profiler.time_operation("simulation"):
        ...     result = simulate(image)
        >>> print(profiler.get_summary())
    """

    def __init__(self):
        """Initialize the profiler."""
        self._timings: dict[str, TimingReport] = {}
        self._enabled = True

    @contextmanager
    def time_operation(self, operation_name: str):
        """Context manager to time an operation.

        Args:
            operation_name: Name of the operation being timed.

        Yields:
            None

        Example:
            >>> profiler = PerformanceProfiler()
            >>> with profiler.time_operation("batch_process"):
            ...     results = process_batch(images)
        """
        if not self._enabled:
            yield
            return

        start_time = time.perf_counter()
        try:
            yield
        finally:
            elapsed_ms = (time.perf_counter() - start_time) * 1000
            self._record(operation_name, elapsed_ms)

    def _record(self, operation_name: str, time_ms: float) -> None:
        """Record a timing measurement.

        Args:
            operation_name: Name of the operation.
            time_ms: Time in milliseconds.
        """
        if operation_name not in self._timings:
            self._timings[operation_name] = TimingReport(operation=operation_name)

        self._timings[operation_name].add_measurement(time_ms)

    def get_report(self, operation_name: str) -> TimingReport | None:
        """Get timing report for a specific operation.

        Args:
            operation_name: Name of the operation.

        Returns:
            TimingReport or None if operation not found.
        """
        return self._timings.get(operation_name)

    def get_all_reports(self) -> dict[str, TimingReport]:
        """Get all timing reports.

        Returns:
            Dictionary mapping operation names to TimingReport objects.
        """
        return self._timings.copy()

    def get_summary(self) -> str:
        """Get a formatted summary of all timings.

        Returns:
            Formatted string with timing summary.
        """
        if not self._timings:
            return "No timing data recorded."

        lines = [
            "Performance Profile Summary",
            "=" * 70,
            f"{'Operation':<25} {'Calls':<8} {'Total (ms)':<12} {'Avg (ms)':<12}",
            "-" * 70,
        ]

        # Sort by total time (descending)
        sorted_timings = sorted(self._timings.values(), key=lambda x: x.total_time_ms, reverse=True)

        for report in sorted_timings:
            lines.append(
                f"{report.operation:<25} {report.call_count:<8} "
                f"{report.total_time_ms:<12.2f} {report.avg_time_ms:<12.2f}"
            )

        total_time = sum(r.total_time_ms for r in self._timings.values())
        lines.append("-" * 70)
        lines.append(f"{'TOTAL':<25} {'':<8} {total_time:<12.2f}")

        return "\n".join(lines)

    def reset(self) -> None:
        """Clear all timing data."""
        self._timings.clear()

    def disable(self) -> None:
        """Disable profiling (no overhead)."""
        self._enabled = False

    def enable(self) -> None:
        """Enable profiling."""
        self._enabled = True

    def to_dict(self) -> dict:
        """Convert all reports to dictionary."""
        return {name: report.to_dict() for name, report in self._timings.items()}


# Global profiler instance for convenience
_global_profiler = PerformanceProfiler()


def time_operation(operation_name: str):
    """Decorator to time a function.

    Args:
        operation_name: Name of the operation.

    Returns:
        Decorated function.

    Example:
        >>> @time_operation("image_simulation")
        ... def simulate_image(image, cvd_type):
        ...     return simulator.simulate(image, cvd_type)
    """

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            with _global_profiler.time_operation(operation_name):
                return func(*args, **kwargs)

        return wrapper

    return decorator


@contextmanager
def timed(operation_name: str):
    """Context manager for timing using the global profiler.

    Args:
        operation_name: Name of the operation.

    Yields:
        None

    Example:
        >>> with timed("batch_processing"):
        ...     results = process_batch(images)
    """
    with _global_profiler.time_operation(operation_name):
        yield


def get_global_profiler() -> PerformanceProfiler:
    """Get the global profiler instance.

    Returns:
        Global PerformanceProfiler instance.
    """
    return _global_profiler


def print_summary() -> None:
    """Print the global profiler summary."""
    print(_global_profiler.get_summary())


def reset_global_profiler() -> None:
    """Reset the global profiler."""
    _global_profiler.reset()


class Timer:
    """Simple timer for manual timing.

    Example:
        >>> timer = Timer()
        >>> timer.start()
        >>> # ... do work ...
        >>> elapsed = timer.stop()
        >>> print(f"Took {elapsed:.2f} ms")
    """

    def __init__(self):
        """Initialize the timer."""
        self._start_time: float | None = None
        self._elapsed_ms: float = 0.0

    def start(self) -> None:
        """Start the timer."""
        self._start_time = time.perf_counter()

    def stop(self) -> float:
        """Stop the timer and return elapsed time.

        Returns:
            Elapsed time in milliseconds.
        """
        if self._start_time is None:
            raise RuntimeError("Timer was not started")

        self._elapsed_ms = (time.perf_counter() - self._start_time) * 1000
        self._start_time = None
        return self._elapsed_ms

    @property
    def elapsed_ms(self) -> float:
        """Get elapsed time in milliseconds."""
        if self._start_time is not None:
            return (time.perf_counter() - self._start_time) * 1000
        return self._elapsed_ms

    def __enter__(self) -> "Timer":
        """Context manager entry."""
        self.start()
        return self

    def __exit__(self, *args) -> None:
        """Context manager exit."""
        self.stop()


def estimate_batch_time(image_count: int, avg_time_per_image_ms: float = 500.0) -> dict[str, float]:
    """Estimate batch processing time.

    Args:
        image_count: Number of images to process.
        avg_time_per_image_ms: Average time per image in milliseconds.

    Returns:
        Dictionary with time estimates.
    """
    total_ms = image_count * avg_time_per_image_ms * 4  # 4 CVD types

    return {
        "total_ms": total_ms,
        "total_seconds": total_ms / 1000,
        "total_minutes": total_ms / (1000 * 60),
        "per_image_ms": avg_time_per_image_ms * 4,
    }


__all__ = [
    "TimingReport",
    "PerformanceProfiler",
    "time_operation",
    "timed",
    "get_global_profiler",
    "print_summary",
    "reset_global_profiler",
    "Timer",
    "estimate_batch_time",
]
