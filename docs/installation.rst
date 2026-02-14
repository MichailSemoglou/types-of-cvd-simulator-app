Installation
============

This page describes how to install CVD Simulator.

Requirements
------------

* Python 3.10 or higher
* pip or conda package manager

From PyPI (Recommended)
-----------------------

Install the latest stable release:

.. code-block:: bash

   pip install cvd-simulator

From Source
-----------

Clone the repository and install in development mode:

.. code-block:: bash

   git clone https://github.com/MichailSemoglou/types-of-cvd-simulator-app.git
   cd types-of-cvd-simulator-app
   pip install -e ".[dev]"

Development Installation
------------------------

For development, install with all optional dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

This installs:

* Testing tools (pytest, coverage, hypothesis)
* Code quality tools (black, flake8, mypy)
* Documentation tools (Sphinx, themes)
* Performance tools (pytest-benchmark)

Dependencies
------------

Core Dependencies
~~~~~~~~~~~~~~~~~

* **daltonlens** (0.1.5): Core CVD simulation algorithms
* **Pillow** (12.1.1): Image processing
* **numpy** (2.4.2): Numerical operations

Optional Dependencies
~~~~~~~~~~~~~~~~~~~~~

* **pydantic** (>=2.0.0): Schema validation (optional)
* **psutil**: System resource monitoring for optimal worker calculation

Verify Installation
-------------------

Test the installation:

.. code-block:: bash

   cvd-simulator --version
   cvd-simulator --list-algorithms

Docker Installation
-------------------

Build and run using Docker:

.. code-block:: bash

   docker build -t cvd-simulator .
   docker run --rm -v $(pwd)/images:/images cvd-simulator /images/photo.jpg
