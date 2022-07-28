.. _ref_user_guide:

==========
User guide
==========
Anyone who wants to use PyFluent-Visualization can import its Python
modules and contribute Python code to control and monitor Ansys Fluent.


..
   This toctreemust be a top level index to get it to show up in
   pydata_sphinx_theme

.. toctree::
   :maxdepth: 1
   :hidden:

   postprocessing


Overview
========
Session objects are the main entry point when using PyFluent, where
one or more Fluent server sessions can be launched simultaneously from the
client. 

**Example 1**

.. code:: python

   solver_session = pyfluent.launch_fluent()

**Example 2**

.. code:: python

   meshing_session = pyfluent.launch_fluent(meshing_mode=True)

Each session object provides access to multiple services, such as boundary
conditions, meshing workflows, an dfield data properties.

PyFluent contains several basic service modules that provide access to core
Fluent capabilities. 

   - General command and query services are encompassed in three modules: 

      + The ``tui`` module is a collection of Python wrappers around
        Fluent's traditional Text User Interface (TUI) command-based
        infrastructure.

      .. code::

         solver_session.tui.define.models.unsteady_2nd_order('yes’)​

      + The ``settings`` module is a Pythonic interface to access Fluent's setup
        and solution objects, where you can, for instance, enable a
        physics-based model for your simulation.

      .. code::

         session.solver.root.setup.models.energy.enabled = True

      + The ``datamodel`` module is a Python interface to access the
        data model-driven aspects of Fluent, such as the meshing workflows.

      .. code::

         import_geometry.arguments.update_dict({'AppendMesh':True})

   - Surface field and mesh data services are available using ``field_data``
     methods, such as the one for getting the surface data for a specified surface.

   .. code:: 

      surface_data = field_data.get_surfaces(surface_ids)​

   - There are general methods available, such as ``health_check``, ``transcript``,
     and ``events`` that provide access to generic features that are useful for
     running your simulation. For instance,

   .. code:: 

      health_check_service.check_health()​​

   or

   .. code:: 

      transcript_service.begin_streaming()​​

   or

   .. code:: 

      events_service.begin_streaming()

   - Finally, there is a ``scheme_eval`` method that provides for evaluating the scheme.

   .. code:: 

      scheme_eval.string_eval("(rp-unsteady?)")​

