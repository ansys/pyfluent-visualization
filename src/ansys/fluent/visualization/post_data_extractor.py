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

"""Module providing data extractor APIs."""

import itertools
from typing import Dict

from ansys.fluent.core.field_data_interfaces import (
    PathlinesFieldDataRequest,
    ScalarFieldDataRequest,
    SurfaceDataType,
    SurfaceFieldDataRequest,
    VectorFieldDataRequest,
)
import numpy as np

from ansys.fluent.interface.post_objects.post_object_definitions import (
    GraphicsDefn,
    PlotDefn,
)


class ServerDataRequestError(RuntimeError):
    """Exception class for server data errors."""

    def __init__(self):
        super().__init__("Error while requesting data from server.")


class FieldDataExtractor:
    """FieldData DataExtractor."""

    def __init__(self, post_object: GraphicsDefn):
        """Instantiate FieldData DataExtractor.

        Parameters
        ----------
        post_object : GraphicsDefn
            Graphics definition object for which data needs to be extracted.
        """
        self._post_object: GraphicsDefn = post_object

    def fetch_data(self, *args, **kwargs):
        """Fetch data for Graphics object.

        Parameters
        ----------
        None

        Returns
        -------
        Dict[int: Dict[str: np.array]]
            Return dictionary of surfaces id to field name to numpy array.
        """
        if self._post_object.__class__.__name__ == "Mesh":
            return self._fetch_mesh_data(self._post_object, *args, **kwargs)
        elif self._post_object.__class__.__name__ == "Surface":
            return self._fetch_surface_data(self._post_object, *args, **kwargs)
        elif self._post_object.__class__.__name__ == "Contour":
            return self._fetch_contour_data(self._post_object, *args, **kwargs)
        elif self._post_object.__class__.__name__ == "Vector":
            return self._fetch_vector_data(self._post_object, *args, **kwargs)
        elif self._post_object.__class__.__name__ == "Pathlines":
            return self._fetch_pathlines_data(self._post_object, *args, **kwargs)

    @staticmethod
    def _fetch_mesh_data(obj, *args, **kwargs):
        if not obj.surfaces():
            raise RuntimeError("Mesh definition is incomplete.")
        obj._pre_display()
        field_data = obj.session.fields.field_data
        transaction = field_data.new_batch()

        surf_request = SurfaceFieldDataRequest(
            surfaces=obj.surfaces(),
            data_types=[SurfaceDataType.Vertices, SurfaceDataType.FacesConnectivity],
            flatten_connectivity=True,
            *args,
            **kwargs,
        )
        transaction.add_requests(surf_request)
        try:
            fields = transaction.get_response()
            surfaces_data = fields.get_field_data(surf_request)
        except Exception as e:
            raise ServerDataRequestError() from e
        finally:
            obj._post_display()
        return surfaces_data

    def _fetch_surface_data(self, obj, *args, **kwargs):
        surface_api = obj._api_helper.surface_api
        surface_api.create_surface_on_server()
        dummy_object = "dummy_object"
        post_session = obj.get_root()
        if (
            obj.definition.type() == "iso-surface"
            and obj.definition.iso_surface.rendering() == "contour"
        ):
            contour = post_session.Contours[dummy_object]
            contour.field = obj.definition.iso_surface.field()
            contour.surfaces = [obj._name]
            contour.show_edges = True
            contour.range.auto_range_on.global_range = True
            surface_data = self._fetch_contour_data(contour)
            del post_session.Contours[dummy_object]
        else:
            mesh = post_session.Meshes[dummy_object]
            mesh.surfaces = [obj._name]
            mesh.show_edges = True
            surface_data = self._fetch_mesh_data(mesh)
        surface_api.delete_surface_on_server()
        return surface_data

    @staticmethod
    def _fetch_contour_data(obj, *args, **kwargs):
        if not obj.surfaces() or not obj.field():
            raise RuntimeError("Contour definition is incomplete.")

        # contour properties
        obj._pre_display()
        field = obj.field()
        node_values = obj.node_values()
        boundary_values = obj.boundary_values()

        field_data = obj.session.fields.field_data
        transaction = field_data.new_batch()
        # get scalar field data
        surf_request = SurfaceFieldDataRequest(
            surfaces=obj.surfaces(),
            data_types=[SurfaceDataType.Vertices, SurfaceDataType.FacesConnectivity],
            flatten_connectivity=True,
            *args,
            **kwargs,
        )
        scalar_request = ScalarFieldDataRequest(
            field_name=field,
            surfaces=obj.surfaces(),
            node_value=node_values,
            boundary_value=boundary_values,
        )
        try:
            fields = transaction.add_requests(
                surf_request, scalar_request
            ).get_response()
            scalar_field_data = fields.get_field_data(scalar_request)
            surface_data = fields.get_field_data(surf_request)
        except Exception as e:
            raise ServerDataRequestError() from e
        finally:
            obj._post_display()
        for k, v in surface_data.items():
            setattr(v, field, scalar_field_data.get(k))
        return surface_data

    @staticmethod
    def _fetch_pathlines_data(obj, *args, **kwargs):
        if not obj.surfaces() or not obj.field():
            raise RuntimeError("Ptahline definition is incomplete.")
        obj._pre_display()
        field = obj.field()
        field_data = obj.session.fields.field_data
        transaction = field_data.new_batch()
        pathlines_request = PathlinesFieldDataRequest(
            surfaces=obj.surfaces(),
            field_name=field,
            flatten_connectivity=True,
        )

        try:
            fields = transaction.add_requests(pathlines_request).get_response()
            pathlines_data = fields.get_field_data(pathlines_request)
        except Exception as e:
            raise ServerDataRequestError() from e
        finally:
            obj._post_display()
        return pathlines_data

    def _fetch_vector_data(self, obj, *args, **kwargs):
        if not obj.surfaces():
            raise RuntimeError("Vector definition is incomplete.")

        obj._pre_display()
        field = obj.field()
        if not field:
            field = obj.field = "velocity-magnitude"
        field_data = obj.session.fields.field_data

        transaction = field_data.new_batch()

        # surface ids
        surfaces_info = field_data.surfaces()

        surf_request = SurfaceFieldDataRequest(
            surfaces=obj.surfaces(),
            data_types=[SurfaceDataType.Vertices, SurfaceDataType.FacesConnectivity],
            flatten_connectivity=True,
            *args,
            **kwargs,
        )
        scalar_request = ScalarFieldDataRequest(
            surfaces=obj.surfaces(),
            field_name=field,
            node_value=False,
            boundary_value=False,
        )
        vector_request = VectorFieldDataRequest(
            surfaces=obj.surfaces(), field_name=obj.vectors_of()
        )
        try:
            fields = transaction.add_requests(
                surf_request, scalar_request, vector_request
            ).get_response()
            # The below is required only for extracting 'vector_scale'
            _vector_field = fields().get(0) or fields()[(("type", "vector-field"),)]
            scalar_field = fields.get_field_data(scalar_request)
            surface_data = fields.get_field_data(surf_request)
            vector_field = fields.get_field_data(vector_request)
            for k, v in surface_data.items():
                setattr(v, field, scalar_field.get(k))
                setattr(v, obj.vectors_of(), vector_field.get(k))
                if surfaces_info.get(k):
                    setattr(
                        v,
                        "vector_scale",
                        _vector_field.get(surfaces_info.get(k)["surface_id"][0])[
                            "vector-scale"
                        ],
                    )
        except Exception as e:
            raise ServerDataRequestError() from e
        finally:
            obj._post_display()
        return surface_data


class XYPlotDataExtractor:
    """XYPlot DataExtractor."""

    def __init__(self, post_object: PlotDefn):
        """Instantiate XYPlot DataExtractor.

        Parameters
        ----------
        post_object : PlotDefn
            Plot definition object for which data needs to be extracted.
        """
        self._post_object: PlotDefn = post_object

    def fetch_data(self) -> Dict[str, Dict[str, np.array]]:
        """Fetch data for visualization object.

        Parameters
        ----------
        None

        Returns
        -------
        Dict[str: Dict[str: np.array]]
            Return dictionary of surfaces name to numpy array of x and y values.
        """

        if self._post_object.__class__.__name__ == "XYPlot":
            return self._fetch_xy_data(self._post_object)

    def _fetch_xy_data(self, obj):
        obj._pre_display()
        field = obj.y_axis_function()
        node_values = obj.node_values()
        boundary_values = obj.boundary_values()
        direction_vector = obj.direction_vector()
        surfaces = obj.surfaces()
        field_data = obj.session.fields.field_data
        transaction = field_data.new_batch()
        surfaces_info = field_data.surfaces()
        surface_ids = [
            id
            for surf in map(obj._api_helper.remote_surface_name, obj.surfaces())
            for id in surfaces_info[surf]["surface_id"]
        ]
        # For group surfaces, expanded surf name is used.
        # If group1 consists of id 3,4,5 then corresponding surface name will be
        # group:3, group:4, group:5
        surfaces_list_expanded = [
            expanded_surf_name
            for expanded_surf_name_list in itertools.starmap(
                lambda local_surface_name, id_list: (
                    [local_surface_name]
                    if len(id_list) == 1
                    else [f"{local_surface_name}:{id}" for id in id_list]
                ),
                [
                    (
                        local_surface_name,
                        surfaces_info[remote_surface_name]["surface_id"],
                    )
                    for remote_surface_name, local_surface_name in zip(
                        map(obj._api_helper.remote_surface_name, surfaces),
                        surfaces,
                    )
                ],
            )
            for expanded_surf_name in expanded_surf_name_list
        ]

        # get scalar field data
        surf_request = SurfaceFieldDataRequest(
            surfaces=surface_ids,
            data_types=(
                [SurfaceDataType.Vertices]
                if node_values
                else [SurfaceDataType.FacesCentroid]
            ),
        )
        scalar_request = ScalarFieldDataRequest(
            field_name=field,
            surfaces=surface_ids,
            node_value=node_values,
            boundary_value=boundary_values,
        )
        xyplot_payload_data = transaction.add_requests(
            surf_request, scalar_request
        ).get_response()
        xyplot_data = xyplot_payload_data.get_field_data(scalar_request)
        surface_data = xyplot_payload_data.get_field_data(surf_request)

        # loop over all surfaces
        xy_plots_data = {}
        surfaces_list_iter = iter(surfaces_list_expanded)
        for surface_id, mesh_data in surface_data.items():
            if node_values:
                mesh_data.vertices.shape = mesh_data.vertices.size // 3, 3
            else:
                mesh_data.centroid.shape = mesh_data.centroid.size // 3, 3
            y_values = xyplot_data[surface_id]
            if y_values is None:
                continue
            x_values = np.matmul(
                mesh_data.vertices if node_values else mesh_data.centroid,
                direction_vector,
            )
            structured_data = np.empty(
                x_values.size,
                dtype={
                    "names": ("xvalues", "yvalues"),
                    "formats": ("f8", "f8"),
                },
            )
            structured_data["xvalues"] = x_values
            structured_data["yvalues"] = y_values
            sort = np.argsort(structured_data, order=["xvalues"])
            surface_name = next(surfaces_list_iter)
            xy_plots_data[surface_name] = structured_data[sort]
        obj._post_display()
        return xy_plots_data
