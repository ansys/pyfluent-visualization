.. _getting_started:

===============
Getting Started
===============
To run pyfluent-visualization, you must have a local licensed copy of Ansys Fluent. 
pyfluent-visualization supports Ansys Fluent versions 2022 R2 or newer.

Visit `Ansys <https://www.ansys.com/>`_ for more information on
getting a licensed copy of Ansys Fluent.

************
Installation
************

Python Module
~~~~~~~~~~~~~
The ``ansys-fluent-visualization`` package supports Python 3.7 through
Python 3.10 on Windows and Linux.

Install the latest release from `PyPi
<https://pypi.org/project/ansys-fluent-visualization/>`_ with:

.. code::

   pip install ansys-fluent-visualization

Alternatively, install the latest from `pyfluent-visualization GitHub
<https://github.com/pyansys/pyfluent-visualization/issues>`_ via:

.. code::

   pip install git+https://github.com/pyansys/pyfluent-visualization.git


For a local "development" version, install with:

.. code::

   git clone https://github.com/pyansys/pyfluent-visualization.git
   cd pyfluent-visualization
   pip install -e .

Follow `README.rst. <https://github.com/pyansys/pyfluent-visualization/blob/main/README.rst>`_ This will allow you to install the PyFluent Visualization ``ansys-fluent-core`` module
and modify it locally and have the changes reflected in your setup
after restarting the Python kernel.

This will allow you to install the PyFluent ``ansys-fluent-visualization`` module
and modify it locally and have the changes reflected in your setup
after restarting the Python kernel.

****************
Launching Fluent
****************

You can launch Fluent from Python using the ``launch_fluent`` function:

.. code:: python

  import ansys.fluent.core as pyfluent
  session = pyfluent.launch_fluent(precision="double", processor_count=2)
  session.check_health()
  session.start_transcript() # Streaming the transcript locally

The ``visualization`` package provides integrations with both
``pyvista`` and ``matplotlib``.

If you want to interact with the Fluent graphical user interface, set the
following environment variable:

.. code::

  set PYFLUENT_SHOW_SERVER_GUI=1    # Windows
  export PYFLUENT_SHOW_SERVER_GUI=1 # Linux (bash)

If you want to print the debug information for development, set the following
environment variable:

.. code:: python

  pyfluent.set_log_level('DEBUG')  # for development, by default only errors are shown
