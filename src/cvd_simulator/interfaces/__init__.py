"""Interface modules for the CVD Simulator application.

This package contains different user interfaces including CLI,
GUI (future), and API (future) interfaces.
"""

from cvd_simulator.interfaces.cli import main, create_parser

__all__ = ["main", "create_parser"]
