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
from ansys.fluent.visualization.registrar import (
    _visualizer,
    get_renderer,
    register_renderer,
)
from ansys.fluent.visualization.renderer import GraphicsWindow


class View(str, Enum):
    XY = "xy"
    XZ = "xz"
    YX = "yx"
    YZ = "yz"
    ZX = "zx"
    ZY = "zy"
    ISOMETRIC = "isometric"


class _ViewWrapper:
    def __init__(self, default=View.ISOMETRIC):
        self._value = default

    def __call__(self):
        return self._value

    def __str__(self):
        return str(self._value)

    def __repr__(self):
        return repr(self._value)

    def __eq__(self, other):
        return self._value == other

    def __getattr__(self, attr):
        # Allows access like config.view.name or config.view.value
        return getattr(self._value, attr)

    def allowed_values(self):
        return list(View)

    def set(self, val):
        if isinstance(val, str):
            val = View(val)
        elif not isinstance(val, View):
            raise TypeError("view must be of type 'View' or str")
        self._value = val


class Config:
    def __init__(self):
        self._interactive = True
        self._view = _ViewWrapper()
        self._single_window = False
        self._two_dimensional_renderer = "pyvista"
        self._three_dimensional_renderer = "pyvista"

    @property
    def interactive(self):
        return self._interactive

    @interactive.setter
    def interactive(self, val: bool):
        self._interactive = bool(val)

    @property
    def single_window(self):
        return self._single_window

    @single_window.setter
    def single_window(self, val: bool):
        self._single_window = bool(val)

    @property
    def view(self):
        return self._view

    @view.setter
    def view(self, val):
        self._view.set(val)

    @property
    def two_dimensional_renderer(self):
        return self._two_dimensional_renderer

    @two_dimensional_renderer.setter
    def two_dimensional_renderer(self, val):
        if isinstance(val, str):
            if val in _visualizer:
                self._two_dimensional_renderer = val
            else:
                raise ValueError(
                    f"{val} is not a valid renderer. Valid renderers are {list(_visualizer)}."
                )

    @property
    def three_dimensional_renderer(self):
        return self._three_dimensional_renderer

    @three_dimensional_renderer.setter
    def three_dimensional_renderer(self, val):
        if isinstance(val, str):
            if val in _visualizer:
                self._three_dimensional_renderer = val
            else:
                raise ValueError(
                    f"{val} is not a valid renderer. Valid renderers are {list(_visualizer)}."
                )

    def get_available_renderers(self):
        return list(_visualizer)


config = Config()
