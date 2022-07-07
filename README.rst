PyFluent Visualization
======================
|pyansys| |pypi| |GH-CI| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-fluent-visualization.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-fluent-visualization
   :alt: PyPI

.. |GH-CI| image:: https://github.com/pyansys/pyfluent-visualization/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pyfluent-visualization/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

Overview
--------
The PyFluent Visualization project provides post-processing and visualization
capabilities for PyFluent using `pyvista <https://docs.pyvista.org/>`_ and
`matplotlib <https://matplotlib.org/>`_.

Documentation and Issues
------------------------
Please see the latest release `documentation <https://fluentvisualization.docs.pyansys.com>`_
page for more details.

Please feel free to post issues and other questions at `PyFluent Visualization Issues
<https://github.com/pyansys/pyfluent-visualization/issues>`_.  This is the best place
to post questions and code.

Installation
------------
The ``ansys-fluent-visualization`` package currently supports Python 3.7 through Python
3.10 on Windows and Linux.

If you're using Python 3.10, install the vtk package from .whl file
`here in Windows <https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-win_amd64.whl>`_ or
`here in Linux <https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl>`_.

Install the latest release from `PyPI
<https://pypi.org/project/ansys-fluent-visualization/>`_ with:

.. code:: console

   pip install ansys-fluent-visualization

Alternatively, install the latest from `pyfluent-visualization GitHub
<https://github.com/pyansys/pyfluent-visualization>`_ via:

.. code:: console

   pip install git+https://github.com/pyansys/pyfluent-visualization.git


If you plan on doing local "development" of PyFluent with Git, then install
with:

.. code:: console

   git clone https://github.com/pyansys/pyfluent-visualization.git
   cd pyfluent-visualization
   pip install pip -U
   pip install -e .

Dependencies
------------
You will need a locally installed licensed copy of ANSYS to run Fluent, with the
first supported version being Ansys 2022 R2.

Getting Started
---------------

Basic Usage
~~~~~~~~~~~

.. code:: python

   from ansys.fluent.visualization.pyvista import Graphics
   graphics = Graphics(session=session)
   temperature_contour = graphics.Contours["contour-temperature"]
   temperature_contour.field = "temperature"
   temperature_contour.surfaces_list = ["in1", "in2", "out1"]
   temperature_contour.display("window-1")

Above code assumes that a PyFluent session has already been created and a Fluent case
with input parameters has been set up. The `Analyzing Your Results
<https://fluentvisualization.docs.pyansys.com/users_guide/postprocessing.html>`_ in
the user guide has a complete example.

License and Acknowledgments
---------------------------
``PyFluent Visualization`` is licensed under the MIT license.

This module, ``ansys-fluent-visualization`` makes no commercial claim over Ansys
whatsoever. This tool extends the functionality of ``Fluent`` by adding a Python
interface to the Fluent without changing the core behavior or license of the original
software.  The use of the interactive Fluent control of ``PyFluent Visualization`` requires
a legally licensed local copy of Ansys.

To get a copy of Ansys, please visit `Ansys <https://www.ansys.com/>`_.
