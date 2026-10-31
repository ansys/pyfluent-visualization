.. _getting_started:

===============
Getting started
===============
To run PyFluent-Visualization, you must have a licensed copy of Ansys Fluent
installed locally. PyFluent-Visualization supports Ansys Fluent 2022 R2 and
later.

For more information on Fluent, visit the `Fluent <https://www.ansys.com/products/fluids/ansys-fluent>`_
page on the Ansys website.

***************
Install package
***************
The ``ansys-fluent-visualization`` package supports Python 3.10 through
Python 3.13 on Windows and Linux.

Install the latest release from `PyPi
<https://pypi.org/project/ansys-fluent-visualization/>`_ with:

.. code::

   pip install ansys-fluent-visualization

Alternatively, install the latest version from the `GitHub
<https://github.com/ansys/pyfluent-visualization>`_ with:

.. code::

   pip install git+https://github.com/ansys/pyfluent-visualization.git


If you plan on doing local *development* of PyFluent-Visualization with Git,
install with:

.. code::

   git clone https://github.com/ansys/pyfluent-visualization.git
   cd pyfluent-visualization
   pip install -e .

Any changes that you make locally are reflected in your setup after you restart
the Python kernel.

.. note::
    PyFluent-Visualization seamlessly integrates with
    `PyVista <https://www.pyvista.org/>`_ and `Matplotlib <https://matplotlib.org/>`_.