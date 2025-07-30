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

from pathlib import Path
import pickle
import sys
from typing import Dict, List, Optional, Union

from ansys.fluent.core.field_data_interfaces import SurfaceDataType
import numpy as np
import pytest

from ansys.fluent.visualization import Graphics, Plots


@pytest.fixture(autouse=True)
def patch_mock_api_helper(mocker) -> None:
    mocker.patch(
        "ansys.fluent.interface.post_objects.post_helper.PostAPIHelper",
        MockAPIHelper,
    )


class MockFieldTransaction:
    def __init__(self, session_data, field_request):
        self.service = session_data
        self.fields_request = field_request

    def add_surfaces_request(
        self,
        surface_ids: List[int],
        overset_mesh: bool = False,
        provide_vertices=True,
        provide_faces=True,
        provide_faces_centroid=False,
        provide_faces_normal=False,
    ) -> None:
        self.fields_request["surf"].append(
            (
                surface_ids,
                overset_mesh,
                provide_vertices,
                provide_faces,
                provide_faces_centroid,
                provide_faces_normal,
            )
        )

    def add_scalar_fields_request(
        self,
        surface_ids: List[int],
        field_name: str,
        node_value: Optional[bool] = True,
        boundary_value: Optional[bool] = False,
    ) -> None:
        self.fields_request["scalar"].append(
            (surface_ids, field_name, node_value, boundary_value)
        )

    def add_vector_fields_request(
        self,
        surface_ids: List[int],
        field_name: str,
    ) -> None:
        self.fields_request["vector"].append((surface_ids, field_name))

    def get_fields(self) -> Dict[int, Dict]:
        fields = {}
        for request_type, requests in self.fields_request.items():
            for request in requests:
                if request_type == "surf":
                    tag_id = 0
                if request_type == "scalar":
                    location_tag = 4 if request[2] else 2
                    boundary_tag = 8 if request[3] else 0
                    tag_id = location_tag | boundary_tag
                if request_type == "vector":
                    tag_id = 0

                field_requests = fields.get(tag_id)
                if not field_requests:
                    field_requests = fields[tag_id] = {}
                surf_ids = request[0]
                for surf_id in surf_ids:
                    surface_requests = field_requests.get(surf_id)
                    if not surface_requests:
                        surface_requests = field_requests[surf_id] = {}
                    surface_requests.update(self.service["fields"][tag_id][surf_id])
        return fields


class MockFieldData:
    def __init__(self, solver_data):
        self._session_data = solver_data
        self._request_to_serve = {"surf": [], "scalar": [], "vector": []}

    def new_transaction(self):
        return MockFieldTransaction(self._session_data, self._request_to_serve)

    def get_surface_data(
        self,
        surface_name: str,
        data_type: Union[SurfaceDataType, int],
        overset_mesh: Optional[bool] = False,
    ) -> Dict:
        surfaces_info = self.surfaces()
        surface_ids = surfaces_info[surface_name]["surface_id"]
        self._request_to_serve["surf"].append(
            (
                surface_ids,
                overset_mesh,
                data_type == SurfaceDataType.Vertices,
                data_type == SurfaceDataType.FacesConnectivity,
                data_type == SurfaceDataType.FacesCentroid,
                data_type == SurfaceDataType.FacesNormal,
            )
        )
        enum_to_field_name = {
            SurfaceDataType.FacesConnectivity: "faces",
            SurfaceDataType.Vertices: "vertices",
            SurfaceDataType.FacesCentroid: "centroid",
            SurfaceDataType.FacesNormal: "face-normal",
        }

        tag_id = 0
        if overset_mesh:
            tag_id = self._payloadTags[FieldDataProtoModule.PayloadTag.OVERSET_MESH]
        return {
            surface_id: self._session_data["fields"][tag_id][surface_id][
                enum_to_field_name[data_type]
            ]
            for surface_id in surface_ids
        }

    class _Scalars:
        def __init__(self, scalar_data):
            self._scalar_data = scalar_data

        @staticmethod
        def range(*args, **kwargs):
            return [0.0, 0.0]

        def __call__(self):
            return self._scalar_data

    @property
    def scalar_fields(self) -> _Scalars:
        return self._Scalars(self._session_data["scalar_fields_info"])

    @property
    def vector_fields(self) -> dict:
        return self._session_data["vector_fields_info"]

    def surfaces(self) -> dict:
        return self._session_data["surfaces_info"]


class MockAPIHelper:
    _session_data = None
    _session_dump = "tests//session.dump"

    class _SurfaceAPI:
        def __init__(self, obj):
            self.obj = None

    def __init__(self, obj=None):
        if not MockAPIHelper._session_data:
            with open(
                str(Path(MockAPIHelper._session_dump).resolve()),
                "rb",
            ) as pickle_obj:
                MockAPIHelper._session_data = pickle.load(pickle_obj)
        self.field_data = lambda: MockFieldData(MockAPIHelper._session_data)
        self.id = lambda: 1


class MockSession:
    _session_data = None
    _session_dump = "tests//session.dump"

    def __init__(self, obj=None):
        if not MockSession._session_data:
            with open(
                str(Path(MockSession._session_dump).resolve()),
                "rb",
            ) as pickle_obj:
                MockSession._session_data = pickle.load(pickle_obj)

        class Fields:
            def __init__(self):
                self.field_data = MockFieldData(MockSession._session_data)

        self.fields = Fields()
        self.field_data = MockFieldData(MockSession._session_data)
        self.id = lambda: 1


def test_field_api():
    pyvista_graphics = Graphics(session=MockSession, post_api_helper=MockAPIHelper)
    contour1 = pyvista_graphics.Contours["contour-1"]

    field_data = contour1._api_helper.field_data()

    surfaces_id = [v["surface_id"][0] for k, v in field_data.surfaces().items()]

    # Get vertices
    vertices_data = field_data.get_surface_data("wall", SurfaceDataType.Vertices)

    transaction = field_data.new_transaction()

    # Get multiple fields
    transaction.add_surfaces_request(
        surfaces_id[:1],
        provide_vertices=True,
        provide_faces_centroid=True,
        provide_faces=False,
    )
    transaction.add_scalar_fields_request(surfaces_id[:1], "temperature", True)
    transaction.add_scalar_fields_request(surfaces_id[:1], "temperature", False)
    fields = transaction.get_fields()

    surface_tag = 0
    vertices = fields[surface_tag][surfaces_id[0]]["vertices"]
    centroid = fields[surface_tag][surfaces_id[0]]["centroid"]

    node_location_tag = 4
    node_data = fields[node_location_tag][surfaces_id[0]]["temperature"]
    element_location_tag = 2
    element_data = fields[element_location_tag][surfaces_id[0]]["temperature"]

    # Compare vertices obtained by different APIs
    np.testing.assert_array_equal(vertices, vertices_data[next(iter(vertices_data))])
    assert len(vertices) == len(node_data) * 3
    assert len(centroid) == len(element_data) * 3


def test_graphics_operations():
    pyvista_graphics1 = Graphics(session=MockSession())
    pyvista_graphics2 = Graphics(session=MockSession())
    contour1 = pyvista_graphics1.Contours["contour-1"]
    contour2 = pyvista_graphics2.Contours["contour-2"]

    # create
    assert pyvista_graphics1 is not pyvista_graphics2
    assert list(pyvista_graphics1.Contours) == ["contour-1"]
    assert list(pyvista_graphics2.Contours) == ["contour-2"]

    contour2.field = "temperature"
    contour2.surfaces = contour2.surfaces.allowed_values

    contour1.field = "pressure"
    contour1.surfaces = contour2.surfaces.allowed_values[0]

    # copy
    pyvista_graphics2.Contours["contour-3"] = contour1()
    contour3 = pyvista_graphics2.Contours["contour-3"]
    assert contour3() == contour1()

    # update
    contour3.update(contour2())
    assert contour3() == contour2()


def test_contour_object():
    pyvista_graphics = Graphics(session=MockSession())
    contour1 = pyvista_graphics.Contours["contour-1"]

    # Should accept all valid surface.
    contour1.surfaces = contour1.surfaces.allowed_values

    # Important. Because there is no type checking so following passes.
    contour1.field = [contour1.field.allowed_values[0]]

    # Should accept all valid fields.
    contour1.field = contour1.field.allowed_values[0]

    # Important. Because there is no type checking so following test passes.
    contour1.node_values = "value should be boolean"

    # Setting filled to False.
    contour1.node_values = False
    assert contour1.node_values() == False
    contour1.filled = False
    assert contour1.node_values() == True

    # node value can not be set to False because Filled is False
    with pytest.raises(ValueError):
        contour1.node_values = False
    assert contour1.node_values() == True

    contour1.filled = True
    contour1.node_values = False
    assert contour1.node_values() == False
    contour1.range.option = "auto-range-off"
    # node_values is True on setting clip_to_range as True
    contour1.range.auto_range_off.clip_to_range = True
    assert contour1.node_values() == True

    contour1.range.option = "auto-range-on"
    assert contour1.range.auto_range_off() is None

    contour1.range.option = "auto-range-off"
    assert contour1.range.auto_range_on() is None


def test_vector_object():
    if sys.version_info > (3, 13):
        pytest.skip(
            "Random AttributeError in Python 3.13.2: "
            "'PyLocalContainer' object has no attribute '_local_collection'"
        )
    pyvista_graphics = Graphics(session=MockSession())
    vector1 = pyvista_graphics.Vectors["contour-1"]
    field_data = vector1._api_helper.field_data()

    assert vector1.surfaces.allowed_values == list(field_data.surfaces().keys())

    vector1.surfaces = vector1.surfaces.allowed_values

    vector1.range.option = "auto-range-on"
    assert vector1.range.auto_range_off() is None

    vector1.range.option = "auto-range-off"
    assert vector1.range.auto_range_on() is None

    range = field_data.scalar_fields.range("velocity-magnitude", False)
    assert range == pytest.approx(
        [
            vector1.range.auto_range_off.minimum(),
            vector1.range.auto_range_off.maximum(),
        ]
    )


def test_surface_object():
    if sys.version_info > (3, 13):
        pytest.skip(
            "Random AttributeError in Python 3.13.2: "
            "'PyLocalContainer' object has no attribute '_local_collection'"
        )
    pyvista_graphics = Graphics(session=MockSession())
    surf1 = pyvista_graphics.Surfaces["surf-1"]

    surf1.definition.type = "iso-surface"
    assert surf1.definition.plane_surface() is None
    surf1.definition.type = "plane-surface"
    assert surf1.definition.iso_surface() is None

    surf1.definition.plane_surface.creation_method = "xy-plane"
    assert surf1.definition.plane_surface.yz_plane() is None
    assert surf1.definition.plane_surface.zx_plane() is None

    surf1.definition.type = "iso-surface"
    iso_surf = surf1.definition.iso_surface

    # Important. Because there is no type checking so following test passes.
    iso_surf.field = [iso_surf.field.allowed_values[0]]

    # New surface should be in allowed values for graphics.
    cont1 = pyvista_graphics.Contours["surf-1"]
    assert "surf-1" in cont1.surfaces.allowed_values

    # New surface is not available in allowed values for plots.
    matplotlib_plots = Plots(session=MockSession(), post_api_helper=MockAPIHelper)
    p1 = matplotlib_plots.XYPlots["p-1"]
    assert "surf-1" not in p1.surfaces.allowed_values

    # With local surface provider it becomes available.
    local_surfaces_provider = Graphics(session=MockSession()).Surfaces
    matplotlib_plots = Plots(
        session=MockSession(),
        post_api_helper=MockAPIHelper,
        local_surfaces_provider=local_surfaces_provider,
    )


def test_create_plot_objects():
    matplotlib_plots1 = Plots(session=MockSession(), post_api_helper=MockAPIHelper)
    matplotlib_plots2 = Plots(session=MockSession(), post_api_helper=MockAPIHelper)
    matplotlib_plots1.XYPlots["p-1"]
    matplotlib_plots2.XYPlots["p-2"]

    assert matplotlib_plots1 is not matplotlib_plots2
    assert matplotlib_plots1.XYPlots is not matplotlib_plots2.XYPlots
    assert list(matplotlib_plots1.XYPlots) == ["p-1"]


def test_xyplot_object():
    matplotlib_plots = Plots(session=MockSession(), post_api_helper=MockAPIHelper)
    p1 = matplotlib_plots.XYPlots["p-1"]
    field_data = p1._api_helper.field_data()

    assert p1.surfaces.allowed_values == list(field_data.surfaces().keys())

    p1.surfaces = p1.surfaces.allowed_values

    assert p1.y_axis_function.allowed_values == list(field_data.scalar_fields())

    # Important. Because there is no type checking so following passes.
    p1.y_axis_function = [p1.y_axis_function.allowed_values[0]]

    p1.y_axis_function = p1.y_axis_function.allowed_values[0]
