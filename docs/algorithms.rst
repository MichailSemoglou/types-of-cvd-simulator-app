Simulation Algorithms
=====================

This page describes the scientifically-validated algorithms used for CVD simulation.

Overview
--------

CVD Simulator implements multiple algorithms based on peer-reviewed research. Each algorithm has different characteristics in terms of accuracy, performance, and handling of severity levels.

Available Algorithms
--------------------

Brettel et al. (1997)
~~~~~~~~~~~~~~~~~~~~~

* **Reference**: Brettel, H., Viénot, F., & Mollon, J. D. (1997). Computerized simulation of color appearance for dichromats. Journal of the Optical Society of America A, 14(10), 2647-2655.

* **Characteristics**:
  - Classic algorithm, widely used
  - Computationally efficient
  - Good for dichromat simulation
  - Binary (on/off) deficiency simulation

* **Use Case**: Best for quick simulations and when computational efficiency is important.

Viénot et al. (1999)
~~~~~~~~~~~~~~~~~~~~

* **Reference**: Viénot, F., Brettel, H., & Mollon, J. D. (1999). Digital video colourmaps for checking the legibility of displays by dichromats. Color Research & Application, 24(4), 243-252.

* **Characteristics**:
  - Improved accuracy for severe deficiencies
  - Better handling of edge cases
  - Slightly more computationally intensive

* **Use Case**: Recommended for severe CVD simulations and when accuracy is critical.

Machado et al. (2009)
~~~~~~~~~~~~~~~~~~~~~

* **Reference**: Machado, G. M., Oliveira, M. M., & Fernandes, L. A. F. (2009). A physiologically-based model for simulation of color vision deficiency. IEEE Transactions on Visualization and Computer Graphics, 15(6), 1291-1298.

* **Characteristics**:
  - Modern approach
  - Handles severity levels well
  - Physiologically-based model
  - Supports variable severity (0.0-1.0)

* **Use Case**: Best overall choice; supports severity adjustment and provides accurate results.

Vischeck
~~~~~~~~

* **Reference**: Based on the popular Vischeck tool (http://www.vischeck.com/)

* **Characteristics**:
  - Matches output from Vischeck tool
  - Useful for compatibility
  - Moderate computational requirements

* **Use Case**: When you need results comparable to the Vischeck tool.

Auto-Select
~~~~~~~~~~~

* **Characteristics**:
  - Automatically chooses the best algorithm
  - Based on deficiency type and severity
  - Combines strengths of different algorithms

* **Use Case**: When you're unsure which algorithm to use; provides good results across all scenarios.

Algorithm Comparison
--------------------

+---------------+-----------+----------+-------------+-------------+
| Algorithm     | Speed     | Accuracy | Severity    | Best For    |
+===============+===========+==========+=============+=============+
| Brettel 1997  | Fast      | Good     | No          | Quick tests |
+---------------+-----------+----------+-------------+-------------+
| Viénot 1999   | Medium    | Better   | Limited     | Severe CVD  |
+---------------+-----------+----------+-------------+-------------+
| Machado 2009  | Medium    | Best     | Yes         | General use |
+---------------+-----------+----------+-------------+-------------+
| Vischeck      | Medium    | Good     | No          | Vischeck    |
|               |           |          |             | compat      |
+---------------+-----------+----------+-------------+-------------+
| Auto-Select   | Varies    | Best     | Yes         | Unknown     |
+---------------+-----------+----------+-------------+-------------+

Selecting an Algorithm
----------------------

For most use cases, we recommend:

1. **Machado 2009** - Best overall performance and accuracy
2. **Auto-Select** - When you want automatic optimization
3. **Viénot 1999** - For severe deficiency simulation
4. **Brettel 1997** - For quick processing of large batches

Usage Example
-------------

.. code-block:: python

   from cvd_simulator import CVDSimulator, SimulationConfig
   from cvd_simulator.enums import Algorithm

   # Use Machado 2009 algorithm
   config = SimulationConfig(
       algorithm=Algorithm.MACHADO_2009,
       severity=0.8
   )
   simulator = CVDSimulator(config)

   # Or use Auto-Select
   config = SimulationConfig(algorithm=Algorithm.AUTO)
   simulator = CVDSimulator(config)
