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

import ansys.fluent.core as pyfluent
from ansys.fluent.core import examples
from ansys.units import VariableCatalog
import pytest

from ansys.fluent.visualization import Vector


@pytest.fixture(scope="module")
def new_solver_session():
    solver = pyfluent.launch_fluent()
    yield solver
    solver.exit()


@pytest.fixture(scope="module")
def new_solver_session_with_exhaust_case_and_data(new_solver_session):
    import_case = examples.download_file(
        file_name="exhaust_system.cas.h5", directory="pyfluent/exhaust_system"
    )

    import_data = examples.download_file(
        file_name="exhaust_system.dat.h5", directory="pyfluent/exhaust_system"
    )
    solver = new_solver_session
    solver.settings.file.read_case(file_name=import_case)
    solver.settings.file.read_data(file_name=import_data)
    return solver


def test_vectors(new_solver_session_with_exhaust_case_and_data):
    solver_session = new_solver_session_with_exhaust_case_and_data
    with pytest.raises(TypeError):
        # Vector.__init__() missing 2 required positional arguments:
        # 'field' and 'surfaces'
        velocity_vector = Vector(solver=solver_session)
    with pytest.warns(
        UserWarning,
        match="Please use a 'field' from the allowed values. "
        "Currently defaulting it to 'velocity'. "
        "Please use the new signature now onwards.",
    ):
        velocity_vector = Vector(
            solver=solver_session, field="pressure", surfaces=["solid_up:1:830"]
        )

    """
    Firstly we should mention that the signature has changed with the meaning.
    Re-generate the message.
    """

    velocity_vector = Vector(
        solver=solver_session,
        field="velocity",
        color_by=VariableCatalog.PRESSURE,
        surfaces=["solid_up:1:830"],
        scale=20,
    )

    assert velocity_vector.field.allowed_values == ["velocity", "relative-velocity"]
    assert len(velocity_vector.surfaces.allowed_values) == 11
