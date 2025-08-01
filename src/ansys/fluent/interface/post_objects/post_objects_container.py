# Copyright (C) 2022 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Module providing visualization objects."""

import inspect

from ansys.fluent.interface.post_objects.meta import PyLocalContainer


class Container:
    """
    Base class for container objects such as Plots or Graphics.

    Parameters
    ----------
    session : object
        Session object.
    container_type : object
        Type of the container (e.g., Plots, Graphics).
    module : object
        Python module containing post definitions.
    post_api_helper : object
        Helper object providing post-processing APIs.
    local_surfaces_provider : object, optional
        Provider of local surfaces, allowing access to surfaces created in
        external modules (e.g., PyVista). Defaults to ``None``.
    """

    def __init__(
        self,
        session,
        container_type,
        module,
        post_api_helper,
        local_surfaces_provider=None,
    ):
        """__init__ method of Container class."""
        session_state = container_type._sessions_state.get(session)
        self._path = container_type.__name__
        if not session_state:
            session_state = self.__dict__
            container_type._sessions_state[session] = session_state
            self.session = session
            self._init_module(self, module, post_api_helper)
        else:
            self.__dict__ = session_state
        self._local_surfaces_provider = lambda: local_surfaces_provider or getattr(
            self, "Surfaces", []
        )

    def get_path(self):
        """Get container path."""
        return self._path

    @property
    def type(self):
        """Type."""
        return "object"

    def update(self, value):
        """Update the value."""
        for name, val in value.items():
            o = getattr(self, name)
            o.update(val)

    def __call__(self, show_attributes=False):
        state = {}
        for name, cls in self.__dict__.items():
            o = getattr(self, name)
            if o is None or name.startswith("_") or name.startswith("__"):
                continue

            if cls.__class__.__name__ == "PyLocalContainer":
                container = o
                if getattr(container, "is_active", True):
                    state[name] = {}
                    for child_name in container:
                        o = container[child_name]
                        if getattr(o, "is_active", True):
                            state[name][child_name] = o()

        return state

    def _init_module(self, obj, mod, post_api_helper):
        """
        Dynamically initializes and attaches containers for classes in a module.

        Args:
            obj: The parent object to which containers are attached.
            mod: The module containing class definitions to process.
            post_api_helper: Helper object for post-processing API interactions.

        This method identifies classes in the module that match certain criteria,
        creates a container for managing instances of these classes, and attaches
        the container to the parent object (`obj`). A `create()` method is also
        dynamically added to each container for creating and initializing new objects.
        """
        # Iterate through all attributes in the module's dictionary
        for name, cls in mod.__dict__.items():
            if cls.__class__.__name__ in (
                "PyLocalNamedObjectMetaAbstract",
            ) and not inspect.isabstract(cls):
                cont = PyLocalContainer(self, cls, post_api_helper, cls.PLURAL)

                # Define a method to add a "create" function to the container
                def _add_create(py_cont):
                    def _create(**kwargs):
                        new_object = py_cont.__getitem__(
                            py_cont._get_unique_chid_name()
                        )
                        # Validate that all kwargs are valid attributes for the object
                        unexpected_args = set(kwargs) - set(new_object())
                        if unexpected_args:
                            raise TypeError(
                                f"create() got an unexpected keyword argument '{next(iter(unexpected_args))}'."  # noqa: E501
                            )
                        for key, value in kwargs.items():
                            if key == "surfaces":
                                value = list(value)
                            setattr(new_object, key, value)
                        return new_object

                    return _create

                # Attach the create method to the container
                setattr(cont, "create", _add_create(cont))
                # Attach the container to the parent object
                setattr(
                    obj,
                    cls.PLURAL,
                    cont,
                )


class Plots(Container):
    """Manages ``Plots`` object containers for a given session.

    This class provides access to containers used for creating and managing
    plot-related objects such as XY plots and monitor plots.

    Parameters
    ----------
    session : object
        Session object.
    module : object
        Python module containing post definitions.
    post_api_helper : object
        Helper object providing post-processing APIs.
    local_surfaces_provider : object, optional
        Provider of local surfaces, allowing access to surfaces created in
        external modules (e.g., Matplotlib). Defaults to ``None``.

    Attributes
    ----------
    XYPlots : dict
        Container for XY plot objects.
    MonitorPlots : dict
        Container for monitor plot objects.
    """

    _sessions_state = {}

    def __init__(self, session, module, post_api_helper, local_surfaces_provider=None):
        """__init__ method of Plots class."""
        super().__init__(
            session, self.__class__, module, post_api_helper, local_surfaces_provider
        )


class Graphics(Container):
    """Manages ``Graphics`` object containers for a given session.

    This class provides access to containers used for creating and managing
    graphics-related objects such as meshes, surfaces, contours, and vectors.

    Parameters
    ----------
    session : object
        Session object.
    module : object
        Python module containing post definitions.
    post_api_helper : object
        Helper object providing post-processing APIs.
    local_surfaces_provider : object, optional
        Provider of local surfaces, allowing access to surfaces created in
        external modules (e.g., PyVista). Defaults to ``None``.

    Attributes
    ----------
    Meshes : dict
        Container for mesh objects.
    Surfaces : dict
        Container for surface objects.
    Contours : dict
        Container for contour objects.
    Vectors : dict
        Container for vector objects.
    """

    _sessions_state = {}

    def __init__(self, session, module, post_api_helper, local_surfaces_provider=None):
        """__init__ method of Graphics class."""
        super().__init__(
            session, self.__class__, module, post_api_helper, local_surfaces_provider
        )

    def add_outline_mesh(self):
        """Add a mesh outline.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        meshes = getattr(self, "Meshes", None)
        if meshes is not None:
            outline_mesh_id = "mesh-outline"
            outline_mesh = meshes[outline_mesh_id]
            outline_mesh.surfaces = [
                k
                for k, v in outline_mesh._api_helper.field_info()
                .get_surfaces_info()
                .items()
                if v["type"] == "zone-surf" and v["zone_type"] != "interior"
            ]
            return outline_mesh
