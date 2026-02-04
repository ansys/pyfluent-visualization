# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
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

from importlib.metadata import version as _version

from ansys.fluent.visualization.config import config as config
from ansys.fluent.visualization.config import get_config as get_config
from ansys.fluent.visualization.config import set_config as set_config
from ansys.fluent.visualization.containers import Contour as Contour
from ansys.fluent.visualization.containers import IsoSurface as IsoSurface
from ansys.fluent.visualization.containers import Mesh as Mesh
from ansys.fluent.visualization.containers import Monitor as Monitor
from ansys.fluent.visualization.containers import Pathline as Pathline
from ansys.fluent.visualization.containers import PlaneSurface as PlaneSurface
from ansys.fluent.visualization.containers import Surface as Surface
from ansys.fluent.visualization.containers import Vector as Vector
from ansys.fluent.visualization.containers import XYPlot as XYPlot
from ansys.fluent.visualization.graphics import Graphics as Graphics
from ansys.fluent.visualization.plotter import Plots as Plots
from ansys.fluent.visualization.registrar import register_renderer as register_renderer
from ansys.fluent.visualization.renderer import GraphicsWindow as GraphicsWindow

_VERSION_INFO = None
__version__ = _version(__name__.replace(".", "-"))


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
