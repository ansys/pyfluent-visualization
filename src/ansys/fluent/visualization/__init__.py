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

"""Python post processing integrations for the Fluent solver."""

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

_VERSION_INFO = None
__version__ = importlib_metadata.version(__name__.replace(".", "-"))


def version_info() -> str:
    """Method returning the version of PyFluent being used.

    Returns
    -------
    str
        The PyFluent version being used.

    Notes
    -----
        Only available in packaged versions. Otherwise it will return __version__.
    """
    return _VERSION_INFO if _VERSION_INFO is not None else __version__


from enum import Enum
import warnings

from ansys.fluent.core.pyfluent_warnings import PyFluentDeprecationWarning

from ansys.fluent.visualization.containers import (  # noqa: F401
    Contour,
    Mesh,
    Monitor,
    Pathline,
    Surface,
    Vector,
    XYPlot,
)
from ansys.fluent.visualization.graphics import Graphics  # noqa: F401
from ansys.fluent.visualization.plotter import Plots  # noqa: F401
from ansys.fluent.visualization.registrar import register_renderer
from ansys.fluent.visualization.renderer import GraphicsWindow


class View(str, Enum):
    """Available view options."""

    XY = "xy"
    XZ = "xz"
    YX = "yx"
    YZ = "yz"
    ZX = "zx"
    ZY = "zy"
    ISOMETRIC = "isometric"


class Config:
    """Set the configuration variables for visualization."""

    def __init__(self):
        """__init__ method of Config class."""
        self._interactive = True
        self._view = View.ISOMETRIC
        self._single_window = False
        self._two_dimensional_renderer = "pyvista"
        self._three_dimensional_renderer = "pyvista"

    @property
    def interactive(self):
        """Boolean flag to access mode (interactive or non-interactive)."""
        return self._interactive

    @interactive.setter
    def interactive(self, val: bool):
        """Set mode (interactive or non-interactive)."""
        self._interactive = bool(val)

    @property
    def single_window(self):
        """Whether single Qt window is activated."""
        return self._single_window

    @single_window.setter
    def single_window(self, val: bool):
        """Activate (or Deactivate) single Qt window."""
        self._single_window = bool(val)

    @property
    def view(self):
        """Returns the camera angle set for displaying graphics."""
        return self._view

    @view.setter
    def view(self, val):
        """Sets the camera angle set for displaying graphics."""
        self._view = View(val)

    @property
    def two_dimensional_renderer(self):
        """Access the default renderer for displaying 2D plots."""
        return self._two_dimensional_renderer

    @two_dimensional_renderer.setter
    def two_dimensional_renderer(self, val):
        """Sets the default renderer for displaying 2D plots."""
        if isinstance(val, str):
            if val in _visualizer:
                self._two_dimensional_renderer = val
            else:
                raise ValueError(
                    f"{val} is not a valid renderer. Valid renderers are {list(_visualizer)}."
                )

    @property
    def three_dimensional_renderer(self):
        """Access the default renderer for displaying 3D graphics."""
        return self._three_dimensional_renderer

    @three_dimensional_renderer.setter
    def three_dimensional_renderer(self, val):
        """Sets the default renderer for displaying 3D graphics."""
        if isinstance(val, str):
            if val in _visualizer:
                self._three_dimensional_renderer = val
            else:
                raise ValueError(
                    f"{val} is not a valid renderer. Valid renderers are {list(_visualizer)}."
                )

    def get_available_renderer_names(self):
        """Access list of available renderers."""
        return list(_visualizer)


config = Config()


def set_config(blocking: bool = False, set_view_on_display: str = "isometric"):
    """Set visualization configuration."""
    warnings.warn(
        "Please use the module level 'config' instead.", PyFluentDeprecationWarning
    )
    config.interactive = not blocking
    config.view = set_view_on_display


def get_config():
    """Get visualization configuration."""
    warnings.warn(
        "Please use the module level 'config' instead.", PyFluentDeprecationWarning
    )
    return {"blocking": not config.interactive, "set_view_on_display": config.view}
