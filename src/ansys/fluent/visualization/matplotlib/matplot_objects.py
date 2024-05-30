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

from ansys.fluent.visualization.matplotlib.matplot_windows_manager import (
    matplot_windows_manager,
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

        from ansys.fluent.visualization.matplotlib import Plots

        matplotlib_plots =  Plots(session)
        plot1 = matplotlib_plots.XYPlots["plot-1"]
        plot1.surfaces_list = ['symmetry', 'wall']
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
        matplot_windows_manager.plot(self, window_id)


class MonitorPlot(MonitorDefn):
    """Provides for displaying monitor plots.

    Parameters
    ----------
    name :

    parent :

    api_helper :


    .. code-block:: python

        from ansys.fluent.visualization.matplotlib import Plots

        matplotlib_plots =  Plots(session)
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
        matplot_windows_manager.plot(self, window_id)
