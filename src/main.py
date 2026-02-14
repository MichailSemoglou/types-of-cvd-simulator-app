#!/usr/bin/env python3
"""Main entry point for the CVD Simulator application.

This module provides the main entry point for running the CVD Simulator
from the command line. It delegates to the CLI interface.
"""

import sys

from cvd_simulator.interfaces.cli import main

if __name__ == "__main__":
    sys.exit(main())