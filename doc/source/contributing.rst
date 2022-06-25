.. _ref_contributing:

============
Contributing
============
Overall guidance on contributing to a PyAnsys library appears in the
`Contributing <https://dev.docs.pyansys.com/how-to/contributing.html>`_ topic
in the *PyAnsys Developer's Guide*. Ensure that you are thoroughly familiar with
it and `Coding Style
<https://dev.docs.pyansys.com/coding-style/index.html#coding-style>`_ before attempting to
contribute to PyFluent.
 
The following contribution information is specific to PyFluent Visualization.

Cloning the PyFluent Visualization Repository
---------------------------------------------
Run this code to clone and install the latest version of PyFluent Visualization in
development mode:

.. code::

   git clone https://github.com/pyansys/pyfluent-visualization.git
   cd pyfluent-visualization
   pip install pip -U
   pip install install_data/ansys_api_fluent-0.1.0-py3-none-any.whl  # till public release
   pip install -e .

Building Documentation
----------------------
To build the documentation locally you need to follow these steps at the root
directory of the repository:

.. code:: 

    pip install -r requirements/requirements_doc.txt
    cd doc
    make html

After the build completes the html documentation is located in the
``_builds/html`` directory and you can load the ``index.html`` into a web
browser.  To clean the documentation you can execute this command:

.. code::

    make clean

Posting Issues
--------------
Use the `PyFluent Visualization Issues <https://github.com/pyansys/pyfluent-visualization/issues>`_
page to submit questions, report bugs, and request new features.


Code Style
----------
PyFluent is compliant with `PyAnsys Development Code Style Guide
<https://dev.docs.pyansys.com/coding_style/index.html>`_.  Code style is checked
by making use of `pre-commit <https://pre-commit.com/>`_. Install this tool and
activate it executing the following commands:

.. code:: bash

   python -m pip install pre-commit
   pre-commit install

Then, you can use the ``style`` rule defined in the ``Makefile``:

.. code:: bash

   make style

Or directly execute `pre-commit <https://pre-commit.com/>`_:

.. code:: bash

    pre-commit run --all-files --show-diff-on-failure
