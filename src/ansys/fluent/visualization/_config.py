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

"""Global configuration state for visualization."""
import warnings

_global_config = {"blocking": False, "set_view_on_display": None}


def get_config() -> dict:
    """Retrieve visualization configuration.

    Returns
    -------
    config : dict
        Keys are parameter names that can be passed to :func:`set_config`.
    """
    import ansys.fluent.visualization as pyviz

    if pyviz.SINGLE_WINDOW:
        _global_config["blocking"] = False
    return _global_config.copy()


def set_config(blocking: bool = False, set_view_on_display: str = "isometric"):
    """Set visualization configuration.

    Parameters
    ----------
    blocking : bool, default=False
        If True, then graphics/plot display will block the current thread.
    set_view_on_display : str, default=None
        If specified, then graphics will always be displayed in the specified view.
        Valid values are xy, xz, yx, yz, zx, zy and isometric.
    """
    import ansys.fluent.visualization as pyviz

    if set_view_on_display not in set_config.allowed_views:
        raise ValueError(
            f"'{set_view_on_display}' is not an allowed view.\n"
            f"Allowed views are: {set_config.allowed_views}"
        )

    if pyviz.SINGLE_WINDOW:
        warnings.warn("'blocking' cannot be set from PyConsole.")
    else:
        _global_config["blocking"] = blocking
    _global_config["set_view_on_display"] = set_view_on_display


set_config.allowed_views = ["xy", "xz", "yx", "yz", "zx", "zy", "isometric"]
