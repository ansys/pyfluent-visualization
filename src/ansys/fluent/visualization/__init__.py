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
PLOTTER = "pyvista"
SINGLE_WINDOW = False


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


from ansys.fluent.visualization._config import get_config, set_config  # noqa: F401
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

# from ansys.fluent.visualization.graphics.graphics_windows import (  # noqa: F401
#     GraphicsWindow,
# )
from ansys.fluent.visualization.plotter import Plots  # noqa: F401

# from ansys.fluent.visualization.plotter.plotter_windows import PlotterWindow
from ansys.fluent.visualization.visualizer import VisualizerWindow
