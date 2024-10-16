"""A DEPRECATED package that provides interfacing Fluent with graphics renderer."""

import warnings

from ansys.fluent.core.warnings import PyFluentDeprecationWarning

warnings.warn(
    "'pyvista' is deprecated. Use 'graphics' instead.",
    PyFluentDeprecationWarning,
)

from ansys.fluent.visualization.graphics.graphics_objects import Graphics  # noqa: F401
from ansys.fluent.visualization.graphics.graphics_windows_manager import (  # noqa: F401
    graphics_windows_manager,
)

pyvista_windows_manager = graphics_windows_manager
