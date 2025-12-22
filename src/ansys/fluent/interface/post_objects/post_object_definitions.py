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

"""Module providing visualization objects definition."""

import abc
from abc import abstractmethod
from collections.abc import Callable, Sequence
import logging
from typing import TYPE_CHECKING, Literal, NamedTuple, Protocol, Self, cast, final

from ansys.fluent.interface.post_objects.meta import (
    Attribute,
    PyLocalNamedObject,
    PyLocalObject,
    PyLocalProperty,
    if_type_checking_instantiate,
)

if TYPE_CHECKING:
    from ansys.fluent.interface.post_objects.post_objects_container import Container

logger = logging.getLogger("pyfluent.post_objects")



class BasePostObjectDefn(Protocol, metaclass=abc.ABCMeta):
    """Base class for visualization objects."""

    # @abc.abstractmethod
    # def get_root(self) -> Container:
    #     raise NotImplementedError

    surfaces: Callable[[], Sequence[str]]

    def _pre_display(self) -> None:
        local_surfaces_provider = self.get_root()._local_surfaces_provider()
        for surf_name in self.surfaces():
            if surf_name in list(local_surfaces_provider):
                surf_obj = local_surfaces_provider[surf_name]
                surf_api = surf_obj._api_helper.surface_api
                surf_api.create_surface_on_server()

    def _post_display(self) -> None:
        local_surfaces_provider = self.get_root()._local_surfaces_provider()
        for surf_name in self.surfaces():
            if surf_name in list(local_surfaces_provider):
                surf_obj = local_surfaces_provider[surf_name]
                surf_api = surf_obj._api_helper.surface_api
                surf_api.delete_surface_on_server()


class GraphicsDefn(BasePostObjectDefn, PyLocalNamedObject, abc.ABC):
    """Abstract base class for graphics objects."""

    @abstractmethod
    def display(self, window_id: str | None = None) -> None:
        """Display graphics.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If not specified, unique ID is used.
        """
        pass


class PlotDefn(BasePostObjectDefn, PyLocalNamedObject, abc.ABC):
    """Abstract base class for plot objects."""

    @abstractmethod
    def plot(self, window_id: str | None = None) -> None:
        """Draw plot.

        Parameters
        ----------
        window_id : str, optional
            Window ID. If not specified, unique ID is used.
        """
        pass


class MonitorDefn(PlotDefn, abc.ABC):
    """Monitor Definition."""

    PLURAL = "Monitors"

    @final
    @if_type_checking_instantiate
    class monitor_set_name(PyLocalProperty[str | None]):
        """Monitor set name."""

        value = None

        @Attribute
        def allowed_values(self) -> list[str]:
            """Monitor set allowed values."""
            return self.monitors.get_monitor_set_names()


class XYPlotDefn(PlotDefn, abc.ABC):
    """XYPlot Definition."""

    PLURAL = "XYPlots"

    @final
    @if_type_checking_instantiate
    class node_values(PyLocalProperty[bool]):
        """Plot nodal values."""

        value = True

    @final
    @if_type_checking_instantiate
    class boundary_values(PyLocalProperty[bool]):
        """Plot Boundary values."""

        value = True

    @final
    @if_type_checking_instantiate
    class direction_vector(PyLocalProperty[tuple[int, int, int]]):
        """Direction Vector."""

        value = (1, 0, 0)

    @final
    @if_type_checking_instantiate
    class y_axis_function(PyLocalProperty[str | None]):
        """Y Axis Function."""

        value = None

        @Attribute
        def allowed_values(self) -> list[str]:
            """Y axis function allowed values."""
            return list(self.field_data.scalar_fields())

    @final
    @if_type_checking_instantiate
    class x_axis_function(PyLocalProperty[Literal["direction-vector"]]):
        """X Axis Function."""

        value = "direction-vector"

        @Attribute
        def allowed_values(self) -> Sequence[Literal["direction-vector"]]:
            """X axis function allowed values."""
            return ["direction-vector"]

    @if_type_checking_instantiate
    class surfaces(PyLocalProperty[list[str]]):
        """List of surfaces for plotting."""

        value = []

        @Attribute
        def allowed_values(self) -> list[str]:
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )


class MeshDefn(GraphicsDefn):
    """Mesh graphics definition."""

    PLURAL = "Meshes"

    @if_type_checking_instantiate
    class surfaces(PyLocalProperty[list[str]]):
        """List of surfaces for mesh graphics."""

        value = []

        @Attribute
        def allowed_values(self) -> list[str]:
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )

    @if_type_checking_instantiate
    class show_edges(PyLocalProperty[bool]):
        """Show edges for mesh."""

        value = False

    @if_type_checking_instantiate
    class show_nodes(PyLocalProperty[bool]):
        """Show nodes for mesh."""

        value = False

    @if_type_checking_instantiate
    class show_faces(PyLocalProperty[bool]):
        """Show faces for mesh."""

        value = True


class PathlinesDefn(GraphicsDefn):
    """Pathlines definition."""

    PLURAL = "Pathlines"

    @if_type_checking_instantiate
    class field(PyLocalProperty[str | None]):
        """Pathlines field."""

        value = None

        @Attribute
        def allowed_values(self) -> list[str]:
            """Field allowed values."""
            return list(self.field_data.scalar_fields())

    @if_type_checking_instantiate
    class surfaces(PyLocalProperty[list[str]]):
        """List of surfaces for pathlines."""

        value = []

        @Attribute
        def allowed_values(self) -> list[str]:
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )


class SurfaceDefn(GraphicsDefn):
    """Surface graphics definition."""

    PLURAL = "Surfaces"

    @property
    def name(self) -> str:
        """Return name of the surface."""
        return self._name

    @if_type_checking_instantiate
    class show_edges(PyLocalProperty[bool]):
        """Show edges for surface."""

        value = True

    class definition(PyLocalObject[Self]):
        """Specify surface definition type."""

        @final
        @if_type_checking_instantiate
        class type(PyLocalProperty[Literal["plane-surface", "iso-surface"]]):
            """Surface type."""

            value = "iso-surface"

            @Attribute
            def allowed_values(self) -> Sequence[Literal["plane-surface", "iso-surface"]]:
                """Surface type allowed values."""
                return ["plane-surface", "iso-surface"]

        @if_type_checking_instantiate
        class plane_surface(PyLocalObject[Self]):
            """Plane surface definition."""

            @Attribute
            def is_active(self) -> bool:
                """Check whether current object is active or not."""
                return self._parent.type() == "plane-surface"

            @final
            @if_type_checking_instantiate
            class creation_method(
                PyLocalProperty[
                    Literal["xy-plane", "yz-plane", "zx-plane", "point-and-normal"]
                ]
            ):
                """Creation Method."""

                value = "xy-plane"

                @Attribute
                def allowed_values(self) -> Sequence[Literal["xy-plane", "yz-plane", "zx-plane", "point-and-normal"]]:
                    """Surface type allowed values."""
                    return ["xy-plane", "yz-plane", "zx-plane", "point-and-normal"]

            @if_type_checking_instantiate
            class point(PyLocalObject[Self]):
                """Point entry for point-and-normal surface."""

                @Attribute
                def is_active(self) -> bool:
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "point-and-normal"

                @if_type_checking_instantiate
                class x(PyLocalProperty[float]):
                    """X value."""

                    value = 0

                    @Attribute
                    def range(self) -> tuple[float, float]:
                        """X value range."""
                        return cast(tuple[float, float], cast(object, self.field_data.scalar_fields.range("x-coordinate", True)))

                @if_type_checking_instantiate
                class y(PyLocalProperty[float]):
                    """Y value."""

                    value = 0

                    @Attribute
                    def range(self) -> tuple[float, float]:
                        """Y value range."""
                        return cast(tuple[float, float], cast(object, self.field_data.scalar_fields.range("y-coordinate", True)))

                @if_type_checking_instantiate
                class z(PyLocalProperty[float]):
                    """Z value."""

                    value = 0

                    @Attribute
                    def range(self) -> tuple[float, float]:
                        """Z value range."""
                        return cast(tuple[float, float], cast(object, self.field_data.scalar_fields.range("z-coordinate", True)))

            @if_type_checking_instantiate
            class normal(PyLocalObject[Self]):
                """Normal entry for point-and-normal surface."""

                @Attribute
                def is_active(self) -> bool:
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "point-and-normal"

                @if_type_checking_instantiate
                class x(PyLocalProperty[float]):
                    """X value."""

                    value = 0

                    @Attribute
                    def range(self) -> list[int]:
                        """X value range."""
                        return [-1, 1]

                @if_type_checking_instantiate
                class y(PyLocalProperty[float]):
                    """Y value."""

                    value = 0

                    @Attribute
                    def range(self) -> list[int]:
                        """Y value range."""
                        return [-1, 1]

                @if_type_checking_instantiate
                class z(PyLocalProperty[float]):
                    """Z value."""

                    value = 0

                    @Attribute
                    def range(self) -> list[int]:
                        """Z value range."""
                        return [-1, 1]

            @if_type_checking_instantiate
            class xy_plane(PyLocalObject[Self]):
                """XY Plane definition."""

                @Attribute
                def is_active(self) -> bool:
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "xy-plane"

                @if_type_checking_instantiate
                class z(PyLocalProperty[float]):
                    """Z value."""

                    value = 0

                    @Attribute
                    def range(self) -> tuple[float, float]:
                        """Z value range."""
                        return self.field_data.scalar_fields.range("z-coordinate", True)

            @if_type_checking_instantiate
            class yz_plane(PyLocalObject[Self]):
                """YZ Plane definition."""

                @Attribute
                def is_active(self) -> bool:
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "yz-plane"

                @if_type_checking_instantiate
                class x(PyLocalProperty[float]):
                    """X value."""

                    value = 0

                    @Attribute
                    def range(self) -> tuple[float, float]:
                        """X value range."""
                        return self.field_data.scalar_fields.range("x-coordinate", True)

            @if_type_checking_instantiate
            class zx_plane(PyLocalObject[Self]):
                """ZX Plane definition."""

                @Attribute
                def is_active(self) -> bool:
                    """Check whether current object is active or not."""
                    return self._parent.creation_method() == "zx-plane"

                @if_type_checking_instantiate
                class y(PyLocalProperty[float]):
                    """Y value."""

                    value = 0

                    @Attribute
                    def range(self) -> tuple[float, float]:
                        """Y value range."""
                        return self.field_data.scalar_fields.range("y-coordinate", True)

        @if_type_checking_instantiate
        class iso_surface(PyLocalObject[Self]):
            """Iso surface definition."""

            @Attribute
            def is_active(self) -> bool:
                """Check whether current object is active or not."""
                return self._parent.type() == "iso-surface"

            @if_type_checking_instantiate
            class field(PyLocalProperty[str | None]):
                """Iso surface field."""

                value = None

                @Attribute
                def allowed_values(self) -> list[str]:
                    """Field allowed values."""
                    return list(self.field_data.scalar_fields())

            @final
            @if_type_checking_instantiate
            class rendering(PyLocalProperty[Literal["mesh", "contour"]]):
                """Iso surface rendering."""

                value = "mesh"

                @Attribute
                def allowed_values(self) -> Sequence[Literal["mesh", "contour"]]:
                    """Surface rendering allowed values."""
                    return ["mesh", "contour"]

            @if_type_checking_instantiate
            class iso_value(PyLocalProperty[float | None]):
                """Iso value for field."""

                _value = None

                def _reset_on_change(self) -> list:
                    return [self._parent.field]

                @property
                def value(self) -> float | None:
                    """Iso value property."""
                    if getattr(self, "_value", None) is None:
                        rnge = self.range
                        self._value = (rnge[0] + rnge[1]) / 2.0 if rnge else None
                    return self._value

                @value.setter
                def value(self, value: float | None) -> None:
                    self._value = value

                @Attribute
                def range(self) -> tuple[float, float] | None:
                    """Iso value range."""
                    field = self._parent.field()
                    if field:
                        return self.field_data.scalar_fields.range(field, True)


class ContourDefn(GraphicsDefn):
    """Contour graphics definition."""

    PLURAL = "Contours"

    @if_type_checking_instantiate
    class field(PyLocalProperty[str | None]):
        """Contour field."""

        value = None

        @Attribute
        def allowed_values(self) -> list[str]:
            """Field allowed values."""
            return list(self.field_data.scalar_fields())

    @if_type_checking_instantiate
    class surfaces(PyLocalProperty[list[str]]):
        """Contour surfaces."""

        value = []

        @Attribute
        def allowed_values(self) -> list[str]:
            """Surfaces list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )

    @if_type_checking_instantiate
    class filled(PyLocalProperty[bool]):
        """Draw filled contour."""

        value = True

    @if_type_checking_instantiate
    class node_values(PyLocalProperty[bool]):
        """Draw nodal data."""

        _value = True

        @Attribute
        def is_active(self) -> bool:
            """Check whether current object is active or not."""
            filled = self.get_ancestors_by_type(ContourDefn).filled()
            auto_range_off = self.get_ancestors_by_type(
                ContourDefn
            ).range.auto_range_off
            if (
                filled is False
                or (auto_range_off and auto_range_off.clip_to_range()) is True
            ):
                return False
            return True

        @property
        def value(self) -> bool:
            """Node value property setter."""
            if self.is_active is False:
                return True
            return self._value

        @value.setter
        def value(self, value: bool) -> None:
            if value is False and self.is_active is False:
                raise ValueError(
                    "For unfilled and clipped contours, node values must be displayed. "
                )
            self._value = value

    @if_type_checking_instantiate
    class boundary_values(PyLocalProperty[bool]):
        """Draw boundary values."""

        value = False

    @if_type_checking_instantiate
    class contour_lines(PyLocalProperty[bool]):
        """Draw contour lines."""

        value = False

    @if_type_checking_instantiate
    class show_edges(PyLocalProperty[bool]):
        """Show edges."""

        value = False

    class range(PyLocalObject[Self]):
        """Range definition."""

        @final
        @if_type_checking_instantiate
        class option(PyLocalProperty[Literal["auto-range-on", "auto-range-off"]]):
            """Range option."""

            value = "auto-range-on"

            @Attribute
            def allowed_values(self) -> Sequence[Literal["auto-range-on", "auto-range-off"]]:
                """Range option allowed values."""
                return ["auto-range-on", "auto-range-off"]

        @if_type_checking_instantiate
        class auto_range_on(PyLocalObject[Self]):
            """Auto range on definition."""

            @Attribute
            def is_active(self) -> bool:
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-on"

            @if_type_checking_instantiate
            class global_range(PyLocalProperty[bool]):
                """Show global range."""

                value = False

        @if_type_checking_instantiate
        class auto_range_off(PyLocalObject[Self]):
            """Auto range off definition."""

            @Attribute
            def is_active(self) -> bool:
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-off"

            @if_type_checking_instantiate
            class clip_to_range(PyLocalProperty[bool]):
                """Clip contour within range."""

                value = False

            @if_type_checking_instantiate
            class minimum(PyLocalProperty[float | None]):
                """Range minimum."""

                _value = None

                def _reset_on_change(self) -> list:
                    return [
                        self.get_ancestors_by_type(ContourDefn).field,
                        self.get_ancestors_by_type(ContourDefn).node_values,
                    ]

                @property
                def value(self) -> float | None:
                    """Range minimum property setter."""
                    if getattr(self, "_value", None) is None:
                        field = self.get_ancestors_by_type(ContourDefn).field()
                        if field:
                            field_data = self.field_data
                            field_range = field_data.scalar_fields.range(
                                field,
                                self.get_ancestors_by_type(ContourDefn).node_values(),
                            )
                            self._value = field_range[0]
                    return self._value

                @value.setter
                def value(self, value: float | None) -> None:
                    self._value = value

            @if_type_checking_instantiate
            class maximum(PyLocalProperty[float | None]):
                """Range maximum."""

                _value = None

                def _reset_on_change(self) -> list:
                    return [
                        self.get_ancestors_by_type(ContourDefn).field,
                        self.get_ancestors_by_type(ContourDefn).node_values,
                    ]

                @property
                def value(self) -> float | None:
                    """Range maximum property setter."""
                    if getattr(self, "_value", None) is None:
                        field = self.get_ancestors_by_type(ContourDefn).field()
                        if field:
                            field_data = self.field_data
                            field_range = field_data.scalar_fields.range(
                                field,
                                self.get_ancestors_by_type(ContourDefn).node_values(),
                            )
                            self._value = field_range[1]

                    return self._value

                @value.setter
                def value(self, value: float | None) -> None:
                    self._value = value


class VectorDefn(GraphicsDefn):
    """Vector graphics definition."""

    PLURAL = "Vectors"

    @if_type_checking_instantiate
    class vectors_of(PyLocalProperty[str | None]):
        """Vector type."""

        value = None

        @Attribute
        def allowed_values(self) -> list[str]:
            """Vectors of allowed values."""
            return list(self.field_data.vector_fields())

    @if_type_checking_instantiate
    class field(PyLocalProperty[str | None]):
        """Vector color field."""

        value = None

        @Attribute
        def allowed_values(self) -> list[str]:
            """Field allowed values."""
            return list(self.field_data.scalar_fields())

    @if_type_checking_instantiate
    class surfaces(PyLocalProperty[list[str]]):
        """List of surfaces for vector graphics."""

        value = []

        @Attribute
        def allowed_values(self) -> list[str]:
            """Surface list allowed values."""
            return list(self.field_data.surfaces()) + list(
                self.get_root()._local_surfaces_provider()
            )

    @if_type_checking_instantiate
    class scale(PyLocalProperty[float]):
        """Vector scale."""

        value = 1.0

    @if_type_checking_instantiate
    class skip(PyLocalProperty[int]):
        """Vector skip."""

        value = 0

    @if_type_checking_instantiate
    class show_edges(PyLocalProperty[bool]):
        """Show edges."""

        value = False

    @if_type_checking_instantiate
    class range(PyLocalObject[Self]):
        """Range definition."""

        @final
        @if_type_checking_instantiate
        class option(PyLocalProperty[Literal["auto-range-on", "auto-range-off"]]):
            """Range option."""

            value = "auto-range-on"

            @Attribute
            def allowed_values(self) -> Sequence[Literal["auto-range-on", "auto-range-off"]]:
                """Range option allowed values."""
                return ["auto-range-on", "auto-range-off"]

        @if_type_checking_instantiate
        class auto_range_on(PyLocalObject[Self]):
            """Auto range on definition."""

            @Attribute
            def is_active(self) -> bool:
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-on"

            @if_type_checking_instantiate
            class global_range(PyLocalProperty[bool]):
                """Show global range."""

                value = False

        @if_type_checking_instantiate
        class auto_range_off(PyLocalObject[Self]):
            """Auto range off definition."""

            @Attribute
            def is_active(self) -> bool:
                """Check whether current object is active or not."""
                return self._parent.option() == "auto-range-off"

            @if_type_checking_instantiate
            class clip_to_range(PyLocalProperty[bool]):
                """Clip vector within range."""

                value = False

            @if_type_checking_instantiate
            class minimum(PyLocalProperty[float | None]):
                """Range minimum."""

                _value = None

                @property
                def value(self) -> float | None:
                    """Range minimum property setter."""
                    if getattr(self, "_value", None) is None:
                        field_data = self.field_data
                        field_range = field_data.scalar_fields.range(
                            "velocity-magnitude",
                            False,
                        )
                        self._value = field_range[0]
                    return self._value

                @value.setter
                def value(self, value: float | None) -> None:
                    self._value = value

            @if_type_checking_instantiate
            class maximum(PyLocalProperty[float | None]):
                """Range maximum."""

                _value = None

                @property
                def value(self) -> float | None:
                    """Range maximum property setter."""
                    if getattr(self, "_value", None) is None:
                        field_data = self.field_data
                        field_range = field_data.scalar_fields.range(
                            "velocity-magnitude",
                            False,
                        )
                        self._value = field_range[1]
                    return self._value

                @value.setter
                def value(self, value: float | None) -> None:
                    self._value = value
