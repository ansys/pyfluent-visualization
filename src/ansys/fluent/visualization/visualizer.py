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

"""A wrapper to improve the user interface of graphics."""
import warnings

import ansys.fluent.visualization as pyviz
from ansys.fluent.visualization.graphics import graphics_windows_manager
from ansys.fluent.visualization.graphics.graphics_windows import GraphicsWindow
from ansys.fluent.visualization.plotter.plotter_windows import PlotterWindow


class VisualizerWindow:
    """Create a graphics window to perform operations like display,
    save, animate, etc. on graphics and plot objects.

    Examples
    --------
    You can add graphics objects like mesh, surface or plots and then display it.

    >>> from ansys.fluent.visualization import VisualizerWindow

    >>> graphics_window = VisualizerWindow()
    >>> graphics_window.add_graphics(mesh_object)
    >>> graphics_window.show()

    You can add multiple graphics objects and display as a structured layout.

    >>> graphics_window = VisualizerWindow()
    >>> graphics_window.add_graphics(mesh_object, position=(0, 0))
    >>> graphics_window.add_graphics(temperature_contour_object, position=(0, 1))
    >>> graphics_window.add_graphics(velocity_vector_object, position=(1, 0))
    >>> graphics_window.add_plot(xy_plot, position=(1, 1))
    >>> graphics_window.show()
    """

    def __init__(self):
        """__init__ method of VisualizerWindow class."""
        self._graphics_objs = []
        self.window_id = None
        self._visualizer = None
        self._list_of_positions = []

    def add_graphics(
        self,
        graphics_obj,
        position: tuple = (0, 0),
        opacity: float = 1,
    ) -> None:
        """Add graphics-data to a window.

        Parameters
        ----------
        graphics_obj: GraphicsDefn
            Object to render in the window.
        position: tuple, optional
            Position of the sub-plot.
        opacity: float, optional
            Transparency of the sub-plot.
        """
        self._list_of_positions.append(position)
        from ansys.fluent.core.post_objects.post_object_definitions import GraphicsDefn

        if isinstance(graphics_obj.obj, GraphicsDefn):
            locals()["object"] = locals().pop("graphics_obj")
            self._graphics_objs.append({**locals()})
        else:
            warnings.warn("Only graphics objects are supported.")

    def add_plot(
        self,
        plot_obj,
        position: tuple = (0, 0),
        title: str = "",
    ) -> None:
        """Add 2D plot-data to a window.

        Parameters
        ----------
        plot_obj: PlotDefn
            Object to render in the window.
        position: tuple, optional
            Position of the sub-plot.
        title: str, optional
            Title of the sub-plot.
        """
        self._list_of_positions.append(position)
        from ansys.fluent.core.post_objects.post_object_definitions import PlotDefn

        if isinstance(plot_obj.obj, PlotDefn):
            locals()["object"] = locals().pop("plot_obj")
            self._graphics_objs.append({**locals()})
        else:
            warnings.warn("Only 2D plot objects are supported.")

    def _all_plt_objs(self):
        from ansys.fluent.core.post_objects.post_object_definitions import PlotDefn

        for obj in self._graphics_objs:
            if not isinstance(obj["object"].obj, PlotDefn):
                return False
        return True

    @staticmethod
    def _show_find_grid_size(points):
        # Extract x and y coordinates separately
        x_coords = {p[0] for p in points}
        y_coords = {p[1] for p in points}

        # Compute grid size
        x_size = len(x_coords)  # Unique x-values count
        y_size = len(y_coords)  # Unique y-values count

        return x_size, y_size

    def show(self, visualizer=None) -> None:
        """Render the objects in window and display the same."""
        self.window_id = graphics_windows_manager._get_unique_window_id()
        if self.window_id not in graphics_windows_manager._post_windows:
            graphics_windows_manager._post_windows[self.window_id] = None
        if self._all_plt_objs() and not pyviz.SINGLE_WINDOW:
            self._visualizer = PlotterWindow(
                grid=self._show_find_grid_size(self._list_of_positions)
            )
            self._visualizer._plot_objs = self._graphics_objs
        else:
            self._visualizer = GraphicsWindow(
                grid=self._show_find_grid_size(self._list_of_positions)
            )
            self._visualizer._graphics_objs = self._graphics_objs
        self._visualizer.show(self.window_id, visualizer=visualizer)

    def save_graphic(
        self,
        filename: str,
    ) -> None:
        """Save a screenshot of the rendering window as a graphic file.

        Parameters
        ----------
        filename : str
            Path to save the graphic file to.
            Supported formats are SVG, EPS, PS, PDF, and TEX.

        Raises
        ------
        ValueError
            If the window does not support the specified format.

        Examples
        --------
        >>> import ansys.fluent.core as pyfluent
        >>> from ansys.fluent.core import examples
        >>> from ansys.fluent.visualization import VisualizerWindow, Vector
        >>>
        >>> import_case = examples.download_file(
        >>> file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
        >>> )
        >>> import_data = examples.download_file(
        >>> file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
        >>> )
        >>>
        >>> solver_session = pyfluent.launch_fluent()
        >>> solver_session.settings.file.read_case(file_name=import_case)
        >>> solver_session.settings.file.read_data(file_name=import_data)
        >>>
        >>> velocity_vector = Vector(
        >>> solver=solver_session, field="pressure", surfaces=["solid_up:1:830"]
        >>> )
        >>> graphics_window = VisualizerWindow()
        >>> graphics_window.add_graphics(velocity_vector)
        >>> graphics_window.save_graphic("saved_vector.svg")
        """
        if self.window_id:
            self._visualizer.save_graphic(filename)

    def refresh(
        self,
        session_id: str | None = "",
        overlay: bool | None = False,
    ) -> None:
        """Refresh windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for refreshing the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are refreshed.
        overlay : bool, Optional
            Overlay graphics over existing graphics.
        """
        if self.window_id:
            self._visualizer.refresh(
                windows_id=[self.window_id], session_id=session_id, overlay=overlay
            )

    def animate(
        self,
        session_id: str | None = "",
    ) -> None:
        """Animate windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for animating the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are animated.

        Raises
        ------
        NotImplementedError
            If not implemented.
        """
        if self.window_id:
            self._visualizer.animate(windows_id=[self.window_id], session_id=session_id)

    def close(
        self,
        session_id: str | None = "",
    ) -> None:
        """Close windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for closing the windows that belong only to this session.
           The default is ``""``, in which case the windows in all sessions
           are closed.
        """
        if self.window_id:
            self._visualizer.close(windows_id=[self.window_id], session_id=session_id)
