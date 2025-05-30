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
    def render(self, data, grid, position, subplot_title, **kwargs) -> None:
        """Render graphics and plots in window.

        Parameters
        ----------
        data : dict
            Data to plot. Data consists the list of x and y
            values for each curve.
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
