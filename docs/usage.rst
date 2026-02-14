Usage Guide
===========

This guide covers how to use CVD Simulator from both the command line and Python API.

Command Line Interface
----------------------

Basic Usage
~~~~~~~~~~~

Process a single image:

.. code-block:: bash

   cvd-simulator input.jpg

Process multiple images:

.. code-block:: bash

   cvd-simulator img1.jpg img2.jpg img3.jpg

Available Options
~~~~~~~~~~~~~~~~~

.. code-block:: text

   cvd-simulator [-h] [-a ALGORITHM] [-s SEVERITY] [-f FORMAT]
                 [-o OUTPUT] [-q QUALITY] [-v] [--log-level LOG_LEVEL]
                 [--log-file LOG_FILE] [-t TYPE]
                 [--list-algorithms] [--list-types] [--version]
                 images [images ...]

Options:

* ``-a, --algorithm``: Simulation algorithm (brettel_1997, vienot_1999, machado_2009, vischeck, auto)
* ``-s, --severity``: Severity level 0.0-1.0 (default: 0.8)
* ``-f, --format``: Output format (jpeg, png, webp, tiff, bmp)
* ``-o, --output``: Output directory (default: ./outputs)
* ``-q, --quality``: JPEG/WebP quality 1-95 (default: 95)
* ``-v, --verbose``: Enable debug logging
* ``-t, --type``: Process only specific CVD type
* ``--list-algorithms``: Show available algorithms
* ``--list-types``: Show available CVD types

Examples
~~~~~~~~

Process with Machado 2009 algorithm:

.. code-block:: bash

   cvd-simulator input.jpg -a machado_2009 -s 0.7

Output as PNG with custom directory:

.. code-block:: bash

   cvd-simulator input.jpg -f png -o ./my_outputs

Process only protan simulation:

.. code-block:: bash

   cvd-simulator input.jpg -t protan

Python API
----------

Basic Example
~~~~~~~~~~~~~

.. code-block:: python

   from pathlib import Path
   from cvd_simulator import CVDSimulator, SimulationConfig
   from cvd_simulator.enums import Algorithm, CVDType

   # Create configuration
   config = SimulationConfig(
       algorithm=Algorithm.MACHADO_2009,
       severity=0.8,
       output_directory=Path("./outputs")
   )

   # Initialize simulator
   simulator = CVDSimulator(config)

   # Process a single image
   results = simulator.process_image(Path("input.jpg"))

   # Access results
   protan_path = results[CVDType.PROTAN]
   deutan_path = results[CVDType.DEUTAN]
   tritan_path = results[CVDType.TRITAN]
   bw_path = results[CVDType.GRAYSCALE]

Advanced Usage
~~~~~~~~~~~~~~

Simulate specific CVD type only:

.. code-block:: python

   from PIL import Image

   image = simulator.loader.load(Path("input.jpg"))
   simulated = simulator.simulate(image, CVDType.PROTAN)
   # simulated is a PIL Image

Batch processing:

.. code-block:: python

   image_paths = [Path("img1.jpg"), Path("img2.jpg")]
   batch_results = simulator.process_batch(image_paths)

Parallel batch processing:

.. code-block:: python

   from cvd_simulator.core.simulator import AsyncCVDSimulator

   simulator = AsyncCVDSimulator(max_workers=4)
   results = simulator.process_batch_parallel(image_paths)

Environment Variables
---------------------

Configure via environment variables (prefix with ``CVD_SIMULATOR_``):

.. code-block:: bash

   export CVD_SIMULATOR_ALGORITHM=MACHADO_2009
   export CVD_SIMULATOR_SEVERITY=0.7
   export CVD_SIMULATOR_OUTPUT_FORMAT=PNG
   export CVD_SIMULATOR_OUTPUT_DIRECTORY=./my_outputs

Then run:

.. code-block:: bash

   cvd-simulator input.jpg

Python:

.. code-block:: python

   import os
   os.environ["CVD_SIMULATOR_SEVERITY"] = "0.7"
   
   from cvd_simulator.config import SimulationConfig
   config = SimulationConfig.from_env()
