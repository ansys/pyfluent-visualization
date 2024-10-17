"""A DEPRECATED package that provides interfacing Fluent with plotters."""

import warnings

from ansys.fluent.core.warnings import PyFluentDeprecationWarning

warnings.warn(
    "'matplotlib' is deprecated. Use 'plotter' instead.",
    PyFluentDeprecationWarning,
)

from ansys.fluent.visualization.plotter.plotter_objects import Plots  # noqa: F401
from ansys.fluent.visualization.plotter.plotter_windows_manager import (  # noqa: F401
    plotter_windows_manager,
)

matplotlib_windows_manager = plotter_windows_manager
