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

*************
Launch Fluent
*************

You can launch Fluent from PyFluent using the ``launch_fluent`` function:

.. code:: python

  import ansys.fluent.core as pyfluent
  session = pyfluent.launch_fluent(precision="double", processor_count=2, mode="solver")
  session.check_health()
  session.start_transcript() # Streaming the transcript locally

PyFluent-Visualization seamlessly integrates with both
`PyVista <https://www.pyvista.org/>`_ and `Matplotlib <https://matplotlib.org/>`_.
Additionally, it offers flexibility to incorporate other open-source data visualization tools,
such as `Plotly <https://plotly.com/python/>`_, see :ref:`ref_configure`

If you want to print the debug information for development, set the following
environment variable:

.. code:: python

  pyfluent.set_log_level('DEBUG')  # for development, by default only errors are shown
