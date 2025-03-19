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

""".. _ref_meshing_session:

Postprocessing mesh
-------------------
This example uses PyVista and Matplotlib to demonstrate PyFluent
postprocessing capabilities. The 3D model in this example
is a mixing elbow that is being meshed, and you can plot it real time.

"""

from ansys.fluent.visualization import set_config

set_config(blocking=False, set_view_on_display="isometric")

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples

from ansys.fluent.visualization.graphics.graphics_windows_manager import (
    FieldDataType,
    graphics_windows_manager,
)
from ansys.fluent.visualization.pyvista import Graphics

meshing = pyfluent.launch_fluent(mode="meshing", ui_mode="gui")
session_id = meshing._fluent_connection._id
graphics = Graphics(session=meshing)
mesh = graphics.Meshes["mesh-1"]

active_window = None
active_window_id = None

import_file_name = examples.download_file("mixing_elbow.pmdb", "pyfluent/mixing_elbow")


def open_window(window_id):
    global active_window, active_window_id
    active_window_id = window_id
    graphics_windows_manager.open_window(window_id)
    active_window = graphics_windows_manager.get_window(window_id)
    active_window.post_object = mesh
    active_window.overlay = True


mesh_data = {}
overlay = True


def plot_mesh(index, field_name, data):
    raise RuntimeError("*****")
    global mesh_data, active_window, overlay
    if active_window is None:
        return
    if data is not None:
        if index in mesh_data:
            mesh_data[index].update({field_name: data})
        else:
            mesh_data[index] = {field_name: data}
        if "vertices" in mesh_data[index] and "faces" in mesh_data[index]:
            active_window.set_data(FieldDataType.Meshes, mesh_data)
            graphics_windows_manager.refresh_windows(
                session_id, [active_window_id], overlay=overlay
            )
            mesh_data = {}
            overlay = True
    else:
        overlay = False


meshing.fields.field_data_streaming.register_callback(plot_mesh)
meshing.fields.field_data_streaming.start(provideBytesStream=True, chunkSize=1024)

open_window("w0")

###
mesh.show_edges = False
meshing.workflow.InitializeWorkflow(WorkflowType="Watertight Geometry")

meshing.workflow.TaskObject["Import Geometry"].Arguments = {
    "FileName": import_file_name,
    "LengthUnit": "in",
}
meshing.workflow.TaskObject["Import Geometry"].Execute()

mesh.show_edges = True
meshing.workflow.TaskObject["Add Local Sizing"].AddChildToTask()
meshing.workflow.TaskObject["Add Local Sizing"].Execute()

####
meshing.workflow.TaskObject["Generate the Surface Mesh"].Arguments = {
    "CFDSurfaceMeshControls": {"MaxSize": 0.1}
}
meshing.workflow.TaskObject["Generate the Surface Mesh"].Execute()

meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(
    SetupTypeChanged=False
)
meshing.workflow.TaskObject["Describe Geometry"].Arguments = {
    "SetupType": "The geometry consists of only fluid regions with no voids"
}
meshing.workflow.TaskObject["Describe Geometry"].UpdateChildTasks(SetupTypeChanged=True)
meshing.workflow.TaskObject["Describe Geometry"].Execute()
meshing.workflow.TaskObject["Update Boundaries"].Arguments = {
    "BoundaryLabelList": ["wall-inlet"],
    "BoundaryLabelTypeList": ["wall"],
    "OldBoundaryLabelList": ["wall-inlet"],
    "OldBoundaryLabelTypeList": ["velocity-inlet"],
}
meshing.workflow.TaskObject["Update Boundaries"].Execute()

###
meshing.workflow.TaskObject["Update Regions"].Execute()

meshing.workflow.TaskObject["Add Boundary Layers"].AddChildToTask()
meshing.workflow.TaskObject["Add Boundary Layers"].InsertCompoundChildTask()
meshing.workflow.TaskObject["smooth-transition_1"].Arguments = {
    "BLControlName": "smooth-transition_1",
}
meshing.workflow.TaskObject["Add Boundary Layers"].Arguments = {}
meshing.workflow.TaskObject["smooth-transition_1"].Execute()

meshing.workflow.TaskObject["Generate the Volume Mesh"].Arguments = {
    "VolumeFill": "poly-hexcore",
    "VolumeFillControls": {
        "HexMaxCellLength": 0.3,
    },
}
meshing.workflow.TaskObject["Generate the Volume Mesh"].Execute()
