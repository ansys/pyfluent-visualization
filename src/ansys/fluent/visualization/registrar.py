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

"""Module for registering and accessing graphics renderers and plotters."""

from ansys.fluent.visualization.plotter.matplotlib.renderer import (
    Plotter as MatplotlibPlotter,
)
from ansys.fluent.visualization.plotter.pyvista.renderer import (
    Plotter as PyVistaPlotter,
)

_renderer = {"matplotlib": MatplotlibPlotter, "pyvista": PyVistaPlotter}


def register_renderer(name, renderer):
    """Register a plotter or graphics renderer."""
    _renderer[name] = renderer


def get_renderer(key: str):
    """Get a registered plotter or graphics renderer by name."""
    return _renderer[key]
