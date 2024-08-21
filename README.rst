PyFluent-Visualization
======================
|pyansys| |pypi| |GH-CI| |MIT| |black| |pre-commit|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |pypi| image:: https://img.shields.io/pypi/v/ansys-fluent-visualization.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/ansys-fluent-visualization
   :alt: PyPI

.. |GH-CI| image:: https://github.com/ansys/pyfluent-visualization/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/pyfluent-visualization/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black

.. |pre-commit| image:: https://results.pre-commit.ci/badge/github/ansys/pyfluent-visualization/main.svg
   :target: https://results.pre-commit.ci/latest/github/ansys/pyfluent-visualization/main
   :alt: pre-commit.ci status

Overview
--------
PyFluent-Visualization provides postprocessing and visualization
capabilities for `PyFluent <https://github.com/ansys/pyfluent>`_
using `PyVista <https://docs.pyvista.org/>`_ and
`Matplotlib <https://matplotlib.org/>`_.

Documentation and issues
------------------------
For comprehensive information on PyFluent-Visualization, see the latest release
`documentation <https://visualization.fluent.docs.pyansys.com>`_.

In the upper right corner of the documentation's title bar, there is an option
for switching from viewing the documentation for the latest stable release
to viewing the documentation for the development version or previously
released versions.

On the `PyFluent Visualization Issues
<https://github.com/ansys/pyfluent-visualization/issues>`_ page, you can create
issues to submit questions, reports burgs, and request new features. To reach
the project support team, email `pyansys.core@ansys.com <pyansys.core@ansys.com>`_.

Installation
------------
The ``ansys-fluent-visualization`` package supports Python 3.10 through Python
3.12 on Windows and Linux.

If you are using Python 3.10, download and install the wheel file for the ``vtk`` package from
`here for Windows <https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-win_amd64.whl>`_
or from `here for Linux <https://github.com/pyvista/pyvista-wheels/raw/main/vtk-9.1.0.dev0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl>`_.

Install the latest release from `PyPI
<https://pypi.org/project/ansys-fluent-visualization/>`_ with:

.. code:: console

   pip install ansys-fluent-visualization

Alternatively, install the latest release from `GitHub
<https://github.com/ansys/pyfluent-visualization>`_ with:

.. code:: console

   pip install git+https://github.com/ansys/pyfluent-visualization.git


If you plan on doing local *development* of PyFluent-Visualization with Git,
install with:

.. code:: console

   git clone https://github.com/ansys/pyfluent-visualization.git
   cd pyfluent-visualization
   pip install pip -U
   pip install -e .

Dependencies
------------
You must have a licensed copy of Ansys Fluent installed locally.
PyFluent-Visualization supports Ansys Fluent 2022 R2 and
later.

Getting started
---------------

Basic usage
~~~~~~~~~~~
The following code assumes that a PyFluent session has already been created
and a Fluent case with input parameters has been set up. For a complete
example, see `Analyzing your results
<https://fluentvisualization.docs.pyansys.com/users_guide/postprocessing.html>`_ in
the PyFluent-Visualization documentation.

.. code:: python

   from ansys.fluent.visualization.pyvista import Graphics
   graphics = Graphics(session=session)
   temperature_contour = graphics.Contours["contour-temperature"]
   temperature_contour.field = "temperature"
   temperature_contour.surfaces_list = ["in1", "in2", "out1"]
   temperature_contour.display("window-1")

Usage in a JupyterLab environment
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
PyFluent-Visualization uses PyVista, which has the ability to display fully
featured plots within a JupyterLab environment using ipyvtklink. Find out
about using ipyvtklink with PyVista `here <https://docs.pyvista.org/user-guide/jupyter/ipyvtk_plotting.html>`

License and acknowledgments
---------------------------
PyFluent-Visualization is licensed under the MIT license.

PyFluent-Visualization makes no commercial claim over Ansys
whatsoever. This tool extends the functionality of Ansys Fluent
by adding a Python interface to Fluent without changing the
core behavior or license of the original software. The use of the
interactive Fluent control of PyFluent-Visualization requires
a legally licensed local copy of Fluent.

For more information on Fluent, visit the `Fluent <https://www.ansys.com/products/fluids/ansys-fluent>`_
page on the Ansys website.
