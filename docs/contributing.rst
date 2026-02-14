Contributing
============

Thank you for your interest in contributing to CVD Simulator!

Development Setup
-----------------

1. Fork and clone the repository::

   git clone https://github.com/MichailSemoglou/types-of-cvd-simulator-app.git

2. Install development dependencies:

.. code-block:: bash

   pip install -e ".[dev]"

3. Run tests to ensure everything works:

.. code-block:: bash

   pytest

Code Style
----------

We use the following tools:

* **black**: Code formatting (line length: 100)
* **flake8**: Linting
* **mypy**: Type checking

Format code before committing:

.. code-block:: bash

   black src tests
def flake8 src tests
   mypy src

Testing
-------

Run all tests:

.. code-block:: bash

   pytest

Run with coverage:

.. code-block:: bash

   pytest --cov=cvd_simulator --cov-report=html

Run benchmarks:

.. code-block:: bash

   pytest tests/benchmarks --benchmark-only

Run property-based tests:

.. code-block:: bash

   pytest tests/property

Pull Request Process
--------------------

1. Create a feature branch
2. Make your changes
3. Add tests for new functionality
4. Update documentation
5. Run all tests and ensure they pass
6. Submit a pull request

Documentation
-------------

Build documentation:

.. code-block:: bash

   cd docs
   make html

View the built documentation:

.. code-block:: bash

   open _build/html/index.html

Commit Messages
---------------

Use clear, descriptive commit messages:

* ``feat: Add new feature``
* ``fix: Fix bug in X``
* ``docs: Update documentation``
* ``test: Add tests for Y``
* ``refactor: Refactor Z for better performance``

Reporting Issues
----------------

When reporting issues, please include:

* Python version
* Operating system
* Steps to reproduce
* Expected vs actual behavior
* Error messages or logs
