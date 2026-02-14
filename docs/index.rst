CVD Simulator Documentation
===========================

Welcome to the CVD Simulator documentation! This is a comprehensive Python package for simulating color vision deficiencies (CVD), including protanopia, deuteranopia, and tritanopia.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   usage
   api
   algorithms
   contributing
   changelog

Quick Start
-----------

Install the package:

.. code-block:: bash

   pip install cvd-simulator

Use from command line:

.. code-block:: bash

   cvd-simulator input.jpg

Use from Python:

.. code-block:: python

   from cvd_simulator import CVDSimulator, SimulationConfig
   from cvd_simulator.enums import Algorithm, CVDType

   config = SimulationConfig(algorithm=Algorithm.MACHADO_2009)
   simulator = CVDSimulator(config)
   results = simulator.process_image("input.jpg")

Features
--------

* **Multiple Simulation Algorithms**: Support for Brettel (1997), Viénot (1999), Machado (2009), Vischeck, and Auto-select
* **All CVD Types**: Simulate protanopia, deuteranopia, tritanopia, and grayscale (achromatopsia)
* **Batch Processing**: Process multiple images efficiently with parallel execution
* **Flexible Configuration**: Configure via code, environment variables, or CLI arguments
* **Security**: Built-in input validation and path sanitization
* **Type Hints**: Fully typed codebase for better IDE support
* **Comprehensive Testing**: Unit, integration, property-based, and benchmark tests

API Reference
-------------

.. autosummary::
   :toctree: _autosummary
   :recursive:

   cvd_simulator

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
