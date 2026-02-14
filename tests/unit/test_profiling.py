"""Unit tests for the performance profiling system."""

import pytest
import time
from cvd_simulator.utils.profiling import (
    TimingReport,
    PerformanceProfiler,
    time_operation,
    timed,
    get_global_profiler,
    reset_global_profiler,
    Timer,
    estimate_batch_time,
)


class TestTimingReport:
    """Tests for TimingReport dataclass."""
    
    def test_timing_report_initialization(self):
        """Test TimingReport initialization."""
        report = TimingReport(operation="test_op")
        
        assert report.operation == "test_op"
        assert report.total_time_ms == 0.0
        assert report.call_count == 0
        assert report.min_time_ms == float('inf')
        assert report.max_time_ms == 0.0
    
    def test_timing_report_avg_calculation(self):
        """Test average time calculation."""
        report = TimingReport(operation="test_op")
        report.add_measurement(100.0)
        report.add_measurement(200.0)
        
        assert report.avg_time_ms == 150.0
    
    def test_timing_report_avg_no_calls(self):
        """Test average with no calls returns 0."""
        report = TimingReport(operation="test_op")
        assert report.avg_time_ms == 0.0
    
    def test_timing_report_min_max(self):
        """Test min and max tracking."""
        report = TimingReport(operation="test_op")
        report.add_measurement(50.0)
        report.add_measurement(150.0)
        report.add_measurement(100.0)
        
        assert report.min_time_ms == 50.0
        assert report.max_time_ms == 150.0
    
    def test_timing_report_to_dict(self):
        """Test conversion to dictionary."""
        report = TimingReport(operation="test_op")
        report.add_measurement(100.0)
        
        data = report.to_dict()
        
        assert data["operation"] == "test_op"
        assert data["call_count"] == 1
        assert "total_time_ms" in data
        assert "avg_time_ms" in data


class TestPerformanceProfiler:
    """Tests for PerformanceProfiler class."""
    
    def test_profiler_initialization(self):
        """Test profiler initialization."""
        profiler = PerformanceProfiler()
        assert profiler._enabled is True
    
    def test_time_operation_context_manager(self):
        """Test timing with context manager."""
        profiler = PerformanceProfiler()
        
        with profiler.time_operation("test_op"):
            time.sleep(0.01)  # 10ms
        
        report = profiler.get_report("test_op")
        assert report is not None
        assert report.call_count == 1
        assert report.total_time_ms >= 10.0
    
    def test_time_operation_disabled(self):
        """Test timing when disabled has no effect."""
        profiler = PerformanceProfiler()
        profiler.disable()
        
        with profiler.time_operation("test_op"):
            time.sleep(0.01)
        
        report = profiler.get_report("test_op")
        assert report is None
    
    def test_multiple_timings(self):
        """Test multiple timing measurements."""
        profiler = PerformanceProfiler()
        
        for _ in range(3):
            with profiler.time_operation("repeated_op"):
                time.sleep(0.001)
        
        report = profiler.get_report("repeated_op")
        assert report.call_count == 3
    
    def test_get_all_reports(self):
        """Test getting all reports."""
        profiler = PerformanceProfiler()
        
        with profiler.time_operation("op1"):
            pass
        with profiler.time_operation("op2"):
            pass
        
        reports = profiler.get_all_reports()
        assert len(reports) == 2
        assert "op1" in reports
        assert "op2" in reports
    
    def test_reset(self):
        """Test resetting profiler."""
        profiler = PerformanceProfiler()
        
        with profiler.time_operation("test_op"):
            pass
        
        profiler.reset()
        assert len(profiler.get_all_reports()) == 0
    
    def test_get_summary_empty(self):
        """Test summary when no timings recorded."""
        profiler = PerformanceProfiler()
        summary = profiler.get_summary()
        
        assert "No timing data" in summary
    
    def test_get_summary_with_data(self):
        """Test summary with timing data."""
        profiler = PerformanceProfiler()
        
        with profiler.time_operation("slow_op"):
            time.sleep(0.02)
        with profiler.time_operation("fast_op"):
            time.sleep(0.01)
        
        summary = profiler.get_summary()
        
        assert "slow_op" in summary
        assert "fast_op" in summary
        assert "TOTAL" in summary


class TestGlobalProfiler:
    """Tests for global profiler functions."""
    
    def test_get_global_profiler(self):
        """Test getting global profiler."""
        profiler = get_global_profiler()
        assert isinstance(profiler, PerformanceProfiler)
    
    def test_reset_global_profiler(self):
        """Test resetting global profiler."""
        with timed("test_op"):
            pass
        
        reset_global_profiler()
        
        profiler = get_global_profiler()
        assert len(profiler.get_all_reports()) == 0


class TestTimer:
    """Tests for Timer class."""
    
    def test_timer_basic(self):
        """Test basic timer usage."""
        timer = Timer()
        
        timer.start()
        time.sleep(0.01)
        elapsed = timer.stop()
        
        assert elapsed >= 10.0  # At least 10ms
        assert timer.elapsed_ms == elapsed
    
    def test_timer_stop_without_start(self):
        """Test stopping timer without starting raises error."""
        timer = Timer()
        
        with pytest.raises(RuntimeError):
            timer.stop()
    
    def test_timer_context_manager(self):
        """Test timer as context manager."""
        with Timer() as timer:
            time.sleep(0.01)
        
        assert timer.elapsed_ms >= 10.0
    
    def test_timer_elapsed_during_timing(self):
        """Test elapsed property during timing."""
        timer = Timer()
        timer.start()
        
        elapsed1 = timer.elapsed_ms
        time.sleep(0.01)
        elapsed2 = timer.elapsed_ms
        
        assert elapsed2 > elapsed1
        
        timer.stop()


class TestEstimateBatchTime:
    """Tests for estimate_batch_time function."""
    
    def test_estimate_batch_time_basic(self):
        """Test basic batch time estimation."""
        estimate = estimate_batch_time(10, 100.0)
        
        assert "total_ms" in estimate
        assert "total_seconds" in estimate
        assert "total_minutes" in estimate
        assert "per_image_ms" in estimate
    
    def test_estimate_batch_time_calculations(self):
        """Test batch time calculations."""
        estimate = estimate_batch_time(5, 100.0)
        
        # 5 images * 100ms * 4 CVD types = 2000ms
        assert estimate["total_ms"] == 2000.0
        assert estimate["total_seconds"] == 2.0
        assert estimate["total_minutes"] == 2.0 / 60.0
        assert estimate["per_image_ms"] == 400.0


class TestTimeOperationDecorator:
    """Tests for time_operation decorator."""
    
    def test_time_operation_decorator(self):
        """Test timing decorator."""
        reset_global_profiler()
        
        @time_operation("decorated_op")
        def slow_function():
            time.sleep(0.01)
        
        slow_function()
        
        profiler = get_global_profiler()
        report = profiler.get_report("decorated_op")
        
        assert report is not None
        assert report.call_count == 1
