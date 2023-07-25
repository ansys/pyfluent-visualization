from typing import List, Optional


class Contour:
    def error_check(self, solver):
        allowed_fields = (
            solver.field_data.get_scalar_field_data.field_name.allowed_values()
        )
        allowed_surfaces = (
            solver.field_data.get_scalar_field_data.surface_name.allowed_values()
        )
        if self.field not in allowed_fields:
            raise ValueError(
                f"{self.field} is not valid field. Valid fields are - {allowed_fields}"
            )
        for surface in self.surfaces:
            if surface not in allowed_surfaces:
                raise ValueError(
                    f"{surface} is not valid surface. Valid surfaces are - {allowed_surfaces}"  # noqa: E501
                )

    def __init__(self, field: str, surfaces: List[str], solver: Optional = None):
        self.field = field
        self.surfaces = surfaces
        if solver:
            self.solver = solver
            self.error_check(self.solver)

    def _get_contour_name(self):
        import time

        return f"Contour_{time.time()}"

    def draw(self, solver, target):
        self.error_check(solver)
        existing_contours = solver.results.graphics.contour.get_object_names()
        graphics_mode = target
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
