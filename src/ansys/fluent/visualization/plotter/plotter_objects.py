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

"""Module providing visualization objects for Matplotlib."""

import sys
from typing import Optional

from ansys.fluent.core.post_objects.meta import Command
from ansys.fluent.core.post_objects.post_helper import PostAPIHelper
from ansys.fluent.core.post_objects.post_object_definitions import (
    MonitorDefn,
    XYPlotDefn,
)
from ansys.fluent.core.post_objects.post_objects_container import (
    Plots as PlotsContainer,
)

from ansys.fluent.visualization.plotter.plotter_windows_manager import (
    plotter_windows_manager,
)


class Plots(PlotsContainer):
    """
    This class provides access to ``Plots`` object containers for a given
    session so that plots can be created.
    """

    def __init__(
        self, session, post_api_helper=PostAPIHelper, local_surfaces_provider=None
    ):
        super().__init__(
            session, sys.modules[__name__], post_api_helper, local_surfaces_provider
        )


class XYPlot(XYPlotDefn):
    """Provides for displaying XY plots.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization import Plots

        plots =  Plots(session)
        plot1 = matplotlib_plots.XYPlots["plot-1"]
        plot1.surfaces = ['symmetry', 'wall']
        plot1.y_axis_function = "temperature"
        plot1.plot("window-0")
    """

    @Command
    def plot(self, window_id: Optional[str] = None):
        """Draw XYPlot.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        """
        plotter_windows_manager.plot(self, window_id)


class MonitorPlot(MonitorDefn):
    """Provides for displaying monitor plots.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization import Plots

        plots =  Plots(session)
        plot1 = matplotlib_plots.Monitors["plot-1"]
        plot1.monitor_set_name = 'residuals'
        plot1.plot("window-0")
    """

    @Command
    def plot(self, window_id: Optional[str] = None):
        """Draw Monitor Plot.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If an ID is not specified, a unique ID is used.
            The default is ``None``.
        """
        plotter_windows_manager.plot(self, window_id)
