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

"""Abstract module providing rendering functionality."""

from abc import ABC, abstractmethod


class AbstractRenderer(ABC):
    """Abstract class for rendering graphics and plots."""

    @abstractmethod
    def render(self, meshes: list[list[dict]]) -> None:
        """Render graphics and plots in a window.

        Parameters
        ----------
        meshes : list[list[dict]]
            A nested list structure defining the layout and content of the graphics
            to be rendered.

            - The outer list represents the number of subplots to be plotted
            into a single plotter window.

            - Each inner list corresponds to a single sub-plot and
            contains multiple surface definitions.

            - Each dictionary in the inner list defines a surface to be plotted,
            with the following keys:

                - 'data': The mesh or 2d plot object to be plotted.
                - 'position': tuple(int, int),  Location of subplot. Defaults to (0, 0).
                - 'opacity': int, Sets the transparency of the subplot. Defaults to 1,
                meaning fully opaque.
                - 'title': str, Title of the subplot.
                - 'kwargs': A dictionary of additional keyword arguments passed
                directly to the plotter.
        """
        pass

    @abstractmethod
    def show(self):
        pass

    @abstractmethod
    def close(self):
        """Close plotter window."""
        pass

    @abstractmethod
    def save_graphic(self, file_name: str):
        """Save graphics to the specified file.

        Parameters
        ----------
        file_name : str
            File name to save graphic.
        """
        pass
