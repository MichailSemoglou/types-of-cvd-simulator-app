"""Video processing module for CVD Simulator.

This module provides video frame extraction and processing capabilities,
enabling CVD simulation on video content through FFmpeg integration.
"""

from __future__ import annotations

import json
import subprocess
import tempfile
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Callable

from cvd_simulator.utils.logging_config import get_logger

if TYPE_CHECKING:
    from cvd_simulator.config import SimulationConfig
    from cvd_simulator.core.simulator import CVDSimulator
    from cvd_simulator.enums import CVDType

logger = get_logger(__name__)


@dataclass
class VideoMetadata:
    """Metadata extracted from a video file.

    Attributes:
        duration: Video duration in seconds.
        fps: Frames per second.
        width: Frame width in pixels.
        height: Frame height in pixels.
        total_frames: Total number of frames.
        codec: Video codec name.
    """

    duration: float
    fps: float
    width: int
    height: int
    total_frames: int
    codec: str


class VideoProcessorError(Exception):
    """Exception raised for video processing errors."""

    pass


class VideoProcessor:
    """Processor for extracting and processing video frames.

    This class uses FFmpeg to extract frames from video files and
    provides hooks for processing those frames through the CVD simulator.

    Example:
        >>> from cvd_simulator.core.video_processor import VideoProcessor
        >>> processor = VideoProcessor()
        >>> metadata = processor.get_metadata("input.mp4")
        >>> print(f"Duration: {metadata.duration}s, FPS: {metadata.fps}")
    """

    def __init__(self, ffmpeg_path: str | None = None):
        """Initialize the video processor.

        Args:
            ffmpeg_path: Path to FFmpeg executable. If None, assumes
                FFmpeg is in the system PATH.
        """
        self.ffmpeg_path = ffmpeg_path or "ffmpeg"
        self._check_ffmpeg()

    def _check_ffmpeg(self) -> None:
        """Verify FFmpeg is available.

        Raises:
            VideoProcessorError: If FFmpeg is not found.
        """
        try:
            result = subprocess.run(
                [self.ffmpeg_path, "-version"], capture_output=True, text=True, check=True
            )
            version_line = result.stdout.split("\n")[0]
            logger.info(f"FFmpeg found: {version_line}")
        except (subprocess.CalledProcessError, FileNotFoundError) as e:
            raise VideoProcessorError(
                f"FFmpeg not found at '{self.ffmpeg_path}'. "
                "Please install FFmpeg and ensure it's in your PATH."
            ) from e

    def get_metadata(self, video_path: Path | str) -> VideoMetadata:
        """Extract metadata from a video file using ffprobe.

        Args:
            video_path: Path to the video file.

        Returns:
            VideoMetadata object with video information.

        Raises:
            VideoProcessorError: If metadata extraction fails.
        """
        video_path = Path(video_path)

        if not video_path.exists():
            raise VideoProcessorError(f"Video file not found: {video_path}")

        ffprobe_path = self.ffmpeg_path.replace("ffmpeg", "ffprobe")

        cmd = [
            ffprobe_path,
            "-v",
            "error",
            "-select_streams",
            "v:0",
            "-show_entries",
            "stream=width,height,r_frame_rate,codec_name",
            "-show_entries",
            "format=duration",
            "-of",
            "json",
            str(video_path),
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            data = json.loads(result.stdout)

            stream = data.get("streams", [{}])[0]
            format_info = data.get("format", {})

            # Parse frame rate (may be a fraction like "30000/1001")
            fps_str = stream.get("r_frame_rate", "30/1")
            if "/" in fps_str:
                num, den = map(int, fps_str.split("/"))
                fps = num / den if den != 0 else 30.0
            else:
                fps = float(fps_str)

            duration = float(format_info.get("duration", 0))
            width = int(stream.get("width", 0))
            height = int(stream.get("height", 0))
            total_frames = int(duration * fps)
            codec = stream.get("codec_name", "unknown")

            metadata = VideoMetadata(
                duration=duration,
                fps=fps,
                width=width,
                height=height,
                total_frames=total_frames,
                codec=codec,
            )

            logger.debug(f"Video metadata: {metadata}")
            return metadata

        except (subprocess.CalledProcessError, json.JSONDecodeError, ValueError) as e:
            raise VideoProcessorError(f"Failed to extract video metadata: {e}") from e

    def extract_frames(
        self,
        video_path: Path | str,
        output_dir: Path | str,
        fps: float | None = None,
        frame_pattern: str = "frame_%06d.png",
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> list[Path]:
        """Extract frames from a video file.

        Args:
            video_path: Path to the video file.
            output_dir: Directory to save extracted frames.
            fps: Frames per second to extract. If None, extracts all frames.
            frame_pattern: Filename pattern for extracted frames.
            progress_callback: Optional callback(current_frame, total_frames).

        Returns:
            List of paths to extracted frame files.

        Raises:
            VideoProcessorError: If frame extraction fails.
        """
        video_path = Path(video_path)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        if not video_path.exists():
            raise VideoProcessorError(f"Video file not found: {video_path}")

        output_pattern = output_dir / frame_pattern

        cmd = [
            self.ffmpeg_path,
            "-i",
            str(video_path),
            "-vsync",
            "0",  # Disable frame duplication/dropping
        ]

        if fps is not None:
            cmd.extend(["-vf", f"fps={fps}"])

        cmd.extend(["-q:v", "2", str(output_pattern)])  # High quality

        logger.info(f"Extracting frames from {video_path} to {output_dir}")

        try:
            # Get metadata for progress reporting
            metadata = self.get_metadata(video_path)
            total_frames = metadata.total_frames if fps is None else int(metadata.duration * fps)

            process = subprocess.Popen(
                cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            # Monitor progress (simplified - FFmpeg doesn't provide easy progress parsing)
            stdout, stderr = process.communicate()

            if process.returncode != 0:
                raise VideoProcessorError(f"FFmpeg error: {stderr}")

            # Get list of extracted frames
            frames = sorted(output_dir.glob("frame_*.png"))

            logger.info(f"Extracted {len(frames)} frames to {output_dir}")

            if progress_callback:
                progress_callback(len(frames), total_frames)

            return frames

        except subprocess.CalledProcessError as e:
            raise VideoProcessorError(f"Failed to extract frames: {e}") from e

    def process_video(
        self,
        video_path: Path | str,
        simulator: CVDSimulator,
        output_path: Path | str,
        cvd_types: list[CVDType] | None = None,
        fps: float | None = None,
        progress_callback: Callable[[int, int], None] | None = None,
    ) -> dict[CVDType, Path]:
        """Process a video file through CVD simulation.

        Extracts frames, applies CVD simulation, and reassembles into video.

        Args:
            video_path: Path to input video.
            simulator: CVDSimulator instance for processing frames.
            output_path: Path for output video.
            cvd_types: List of CVD types to simulate. If None, processes all types.
            fps: Frames per second to process. If None, uses original FPS.
            progress_callback: Optional callback(frame_num, total_frames).

        Returns:
            Dictionary with output paths and metadata.
        """
        from cvd_simulator.enums import CVDType

        video_path = Path(video_path)
        output_path = Path(output_path)

        if cvd_types is None:
            cvd_types = list(CVDType)

        metadata = self.get_metadata(video_path)

        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            frames_dir = temp_path / "frames"
            processed_dir = temp_path / "processed"

            # Extract frames
            logger.info("Extracting frames...")
            frames = self.extract_frames(video_path, frames_dir, fps=fps or metadata.fps)

            results = {}

            for cvd_type in cvd_types:
                cvd_output_dir = processed_dir / cvd_type.name.lower()
                cvd_output_dir.mkdir(parents=True, exist_ok=True)

                logger.info(f"Processing {cvd_type.name} simulation...")

                # Process each frame
                from PIL import Image

                for i, frame_path in enumerate(frames):
                    # Load and process frame
                    frame = Image.open(frame_path)
                    simulated = simulator.simulate(frame, cvd_type)

                    # Save processed frame
                    output_frame = cvd_output_dir / f"frame_{i:06d}.png"
                    simulated.save(output_frame)

                    if progress_callback:
                        progress_callback(i + 1, len(frames))

                # Reassemble video
                cvd_output_video = (
                    output_path.parent
                    / f"{output_path.stem}_{cvd_type.name.lower()}{output_path.suffix}"
                )
                self._assemble_video(cvd_output_dir, cvd_output_video, fps=fps or metadata.fps)

                results[cvd_type] = cvd_output_video

        return results

    def _assemble_video(self, frames_dir: Path, output_path: Path, fps: float) -> None:
        """Reassemble frames into a video file.

        Args:
            frames_dir: Directory containing frame files.
            output_path: Path for output video.
            fps: Frames per second for output video.
        """
        output_path.parent.mkdir(parents=True, exist_ok=True)

        frame_pattern = frames_dir / "frame_%06d.png"

        cmd = [
            self.ffmpeg_path,
            "-framerate",
            str(fps),
            "-i",
            str(frame_pattern),
            "-c:v",
            "libx264",
            "-pix_fmt",
            "yuv420p",
            "-crf",
            "18",  # High quality
            "-y",  # Overwrite output
            str(output_path),
        ]

        logger.info(f"Assembling video: {output_path}")

        try:
            subprocess.run(cmd, check=True, capture_output=True)
            logger.info(f"Video saved: {output_path}")
        except subprocess.CalledProcessError as e:
            raise VideoProcessorError(f"Failed to assemble video: {e}") from e


__all__ = ["VideoProcessor", "VideoMetadata", "VideoProcessorError"]
