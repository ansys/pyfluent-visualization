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

"""Provides a module for post objects."""

import re

from ansys.fluent.core.solver.flunits import get_si_unit_for_fluent_quantity
from ansys.fluent.core.utils.fluent_version import FluentVersion


class IncompleteISOSurfaceDefinition(RuntimeError):
    """Raised when iso-surface definition is incomplete."""

    def __init__(self):
        """Initialize IncompleteISOSurfaceDefinition."""
        super().__init__("Iso surface definition is incomplete.")


class SurfaceCreationError(RuntimeError):
    """Raised when surface creation is unsuccessful."""

    def __init__(self):
        """Initialize SurfaceCreationError."""
        super().__init__("Surface creation is unsuccessful.")


class PostAPIHelper:
    """Class providing helper API for post objects."""

    class _SurfaceAPI:
        """Class providing APIs for surface operations."""

        def __init__(self, obj):
            self.obj = obj
            self._surface_name_on_server = self.surface_name_on_server(obj._name)

        @staticmethod
        def surface_name_on_server(local_surface_name):
            """Return the surface name on server."""
            return local_surface_name.lower()

        def _get_api_handle(self):
            return self.obj.get_root().session.results.surfaces

        def _delete_if_exists_on_server(self):
            field_info = self.obj._api_helper.field_info()
            surfaces_list = list(field_info.get_surfaces_info().keys())
            if self._surface_name_on_server in surfaces_list:
                self.delete_surface_on_server()

        def create_surface_on_server(self):
            """Create the surface on server.

            Raises
            ------
            IncompleteISOSurfaceDefinition
                If iso-surface definition is incomplete.
            SurfaceCreationError
                If server fails to create surface.
            """
            if self.obj.definition.type() == "iso-surface":
                iso_surface = self.obj.definition.iso_surface
                field = iso_surface.field()
                iso_value = iso_surface.iso_value()
                if not field:
                    raise IncompleteISOSurfaceDefinition()
                self._delete_if_exists_on_server()
                self._get_api_handle().iso_surface[self._surface_name_on_server] = {
                    "field": field,
                    "iso_values": [iso_value],
                }
            elif self.obj.definition.type() == "plane-surface":
                plane_surface = self.obj.definition.plane_surface
                if plane_surface.creation_method() == "point-and-normal":
                    self._get_api_handle().plane_surface[
                        self._surface_name_on_server
                    ] = {
                        "method": "point-and-normal",
                        "normal": [
                            plane_surface.normal.x(),
                            plane_surface.normal.y(),
                            plane_surface.normal.z(),
                        ],
                        "point": [
                            plane_surface.point.x(),
                            plane_surface.point.y(),
                            plane_surface.point.z(),
                        ],
                    }
                else:
                    xy_plane = plane_surface.xy_plane
                    yz_plane = plane_surface.yz_plane
                    zx_plane = plane_surface.zx_plane
                    self._delete_if_exists_on_server()
                    if xy_plane():
                        method = "xy-plane"
                        position = "z"
                        value = xy_plane.z()
                    elif yz_plane():
                        method = "yz-plane"
                        position = "x"
                        value = yz_plane.x()
                    else:
                        method = "zx-plane"
                        position = "y"
                        value = zx_plane.y()
                    self._get_api_handle().plane_surface[
                        self._surface_name_on_server
                    ] = {
                        "method": method,
                        position: value,
                    }
            field_info = self.obj._api_helper.field_info()
            surfaces_list = list(field_info.get_surfaces_info().keys())
            if self._surface_name_on_server not in surfaces_list:
                raise SurfaceCreationError()

        def delete_surface_on_server(self):
            """Deletes the surface on server."""
            if self.obj.definition.type() == "iso-surface":
                del self._get_api_handle().iso_surface[self._surface_name_on_server]
            elif self.obj.definition.type() == "plane-surface":
                del self._get_api_handle().plane_surface[self._surface_name_on_server]

    def __init__(self, obj):
        """__init__ method of PostAPIHelper class."""
        self.obj = obj
        self.field_info = lambda: obj.get_root().session.fields.field_info
        self.field_data = lambda: obj.get_root().session.fields.field_data
        if obj.__class__.__name__ == "Surface":
            self.surface_api = PostAPIHelper._SurfaceAPI(obj)

    def remote_surface_name(self, local_surface_name):
        """Return the surface name."""

        local_surfaces_provider = self.obj.get_root()._local_surfaces_provider()

        if local_surface_name in list(local_surfaces_provider):
            return PostAPIHelper._SurfaceAPI.surface_name_on_server(local_surface_name)
        else:
            return local_surface_name

    def get_field_unit(self, field):
        """Return the unit of the field."""
        session = self.obj.get_root().session
        if FluentVersion(session.scheme_eval.version) < FluentVersion.v252:
            quantity = self._field_unit_quantity(field)
            if quantity == "*null*":
                return ""
            scheme_eval_str = f"(units/get-pretty-wb-units-from-dimension (units/inquire-dimension '{quantity}))"  # noqa: E501
            return " ".join(self._scheme_str_to_py_list(scheme_eval_str))
        else:
            fields_info = self.field_info().get_scalar_fields_info()
            return get_si_unit_for_fluent_quantity(fields_info[field]["quantity_name"])

    def _field_unit_quantity(self, field):
        scheme_eval_str = f"(cdr (assq 'units (%fill-render-info '{field})))"
        return self._scheme_str_to_py_list(scheme_eval_str)[0]

    def _scheme_str_to_py_list(self, scheme_eval_str):
        session = self.obj.get_root().session
        if hasattr(session, "scheme_eval"):
            str_val = session.scheme_eval.string_eval(scheme_eval_str)
            return list(filter(None, re.split(r'[\s()"\']', str_val)))
        else:
            return ["*null*"]
