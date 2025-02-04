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

"""Contour objects based on field name and surfaces list."""

from typing import List, Optional


class Contour:
    """Provides contour objects based on field name and surfaces list.

    Parameters
    ----------
    field : str
        Field name.

    surfaces : List[str]
        List of surfaces.
    """

    def _error_check(self, solver):
        """
        Check field and surface names.
        """
        allowed_fields = (
            solver.field_data.get_scalar_field_data.field_name.allowed_values()
        )
        allowed_surfaces = (
            solver.field_data.get_scalar_field_data.surface_name.allowed_values()
        )
        if self.field not in allowed_fields:
            raise ValueError(
                f"{self.field} is not valid field. Valid fields are {allowed_fields}"
            )
        for surface in self.surfaces:
            if surface not in allowed_surfaces:
                raise ValueError(
                    f"{surface} is not valid surface. Valid surfaces are {allowed_surfaces}"  # noqa: E501
                )

    def __init__(self, field: str, surfaces: List[str], solver: Optional = None):
        """Create contour using field name and surfaces list.

        Parameters
        ----------
        field : str
            Field name.
        surfaces : List[str]
            List of surfaces.
        solver : Optional
            Solver session.
        """
        self.field = field
        self.surfaces = surfaces
        if solver:
            self.solver = solver
            self._error_check(self.solver)

    def _get_contour_name(self):
        """Get random contour name."""
        import time

        return f"Contour_{time.time()}"

    def draw(self, solver, target):
        """Create a Graphics or solver-based contour object.

        Parameters
        ----------
        solver :
            Solver session.
        target :
            Either Graphics object or a solver session.

        Returns
        -------
        Graphics or solver-based contour object.
        """
        self._error_check(solver)
        graphics_mode = target
        existing_contours = (
            solver.results.graphics.contour.get_object_names()
            if graphics_mode.__class__.__name__ == "Solver"
            else graphics_mode.Contours.allowed_values()
        )
        contour_name = self._get_contour_name()
        if contour_name not in existing_contours:
            if graphics_mode.__class__.__name__ == "Graphics":
                contour = graphics_mode.Contours[contour_name]
                contour.field = self.field
                contour.surfaces = self.surfaces
                contour.display()
                return contour
            elif graphics_mode.__class__.__name__ == "Solver":
                solver.results.graphics.contour[contour_name] = {
                    "field": self.field,
                    "surfaces": self.surfaces,
                }
                solver.results.graphics.contour.display(object_name=contour_name)
                return solver.results.graphics.contour[contour_name]
