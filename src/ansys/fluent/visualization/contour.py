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
                contour.surfaces_list = self.surfaces
                contour.display()
                return contour
            elif graphics_mode.__class__.__name__ == "Solver":
                solver.results.graphics.contour[contour_name] = {
                    "field": self.field,
                    "surfaces_list": self.surfaces,
                }
                solver.results.graphics.contour.display(object_name=contour_name)
                return solver.results.graphics.contour[contour_name]
