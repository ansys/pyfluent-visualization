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

"""Module providing visualization objects for PyVista."""

import sys
from typing import Optional

from ansys.fluent.core.post_objects.meta import Command
from ansys.fluent.core.post_objects.post_helper import PostAPIHelper
from ansys.fluent.core.post_objects.post_object_definitions import (
    ContourDefn,
    MeshDefn,
    PathlinesDefn,
    SurfaceDefn,
    VectorDefn,
)
from ansys.fluent.core.post_objects.post_objects_container import (
    Graphics as GraphicsContainer,
)

from ansys.fluent.visualization.graphics.graphics_windows_manager import (
    graphics_windows_manager,
)


class Graphics(GraphicsContainer):
    """
    This class provides access to ``Graphics`` object containers for a given
    session so that graphics objects can be created.
    """

    def __init__(
        self, session, post_api_helper=PostAPIHelper, local_surfaces_provider=None
    ):
        super().__init__(
            session, sys.modules[__name__], post_api_helper, local_surfaces_provider
        )


class Mesh(MeshDefn):
    """Provides for displaying mesh graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization import  Graphics

        graphics_session = Graphics(session)
        mesh1 = graphics_session.Meshes["mesh-1"]
        mesh1.show_edges = True
        mesh1.surfaces = ['wall']
        mesh1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display mesh graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        graphics_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Pathlines(PathlinesDefn):
    """Pathlines definition for PyVista.

    .. code-block:: python

        from ansys.fluent.visualization import  Graphics

        graphics_session = Graphics(session)
        pathlines1 = graphics_session.Pathlines["pathlines-1"]
        pathlines1.field = "velocity-magnitude"
        pathlines1.surfaces = ['inlet']
        pathlines1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display mesh graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        graphics_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Surface(SurfaceDefn):
    """Provides for displaying surface graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization import Graphics

        graphics_session = Graphics(session)
        surface1 = graphics_session.Surfaces["surface-1"]
        surface1.definition.type = "iso-surface"
        surface1.definition.iso_surface.field= "velocity-magnitude"
        surface1.definition.iso_surface.rendering= "contour"
        surface1.definition.iso_surface.iso_value = 0.0
        surface1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display surface graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        graphics_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Contour(ContourDefn):
    """Provides for displaying contour graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization import  Graphics

        graphics_session = Graphics(session)
        contour1 = graphics_session.Contours["contour-1"]
        contour1.field = "velocity-magnitude"
        contour1.surfaces = ['wall']
        contour1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display contour graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        graphics_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )


class Vector(VectorDefn):
    """Provides for displaying vector graphics.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization import  Graphics

        graphics_session = Graphics(session)
        vector1 = graphics_session.Vectors["vector-1"]
        vector1.surfaces = ['symmetry']
        vector1.scale = 4.0
        vector1.skip = 4
        vector1.display("window-0")
    """

    @Command
    def display(self, window_id: Optional[str] = None, overlay: Optional[bool] = False):
        """Display vector graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        overlay : bool, optional
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        graphics_windows_manager.plot(
            self, window_id=window_id, overlay=overlay, fetch_data=True
        )
