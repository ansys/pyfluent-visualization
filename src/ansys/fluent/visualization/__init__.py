"""Python post processing integrations for the Fluent solver."""
import platform
import struct
import sys

import pkg_resources

try:
    import importlib.metadata as importlib_metadata
except ModuleNotFoundError:
    import importlib_metadata

_VERSION_INFO = None
__version__ = importlib_metadata.version(__name__.replace(".", "-"))


def version_info() -> str:
    """Method returning the version of PyFluent being used.
    Returns
    -------
    str
        The PyFluent version being used.
    Notes
    -------
    Only available in packaged versions. Otherwise it will return __version__.
    """
    return _VERSION_INFO if _VERSION_INFO is not None else __version__


required_libraries = {
    "vtk": "9.2.6",
    "pyvista": "0.39.0",
    "pyvistaqt": "0.7.0",
    "pyside6": "6.2.3",
    "matplotlib": "3.5.1",
}


installed = {pkg.key for pkg in pkg_resources.working_set}
installed_libraries = [
    lib for lib, version in required_libraries.items() if lib in installed
]
missing_libraries = required_libraries.keys() - installed
import_errors = []
if missing_libraries:
    import_errors.append(
        (f"Required libraries {missing_libraries} " "are missing to use this feature.")
    )
    for lib in missing_libraries:
        import_errors.append(
            (
                f"  Please install {lib} with "
                f"`pip install {lib}=={required_libraries[lib]}`."
            )
        )
if installed_libraries:
    versions_mismatched_message = False
    for lib in installed_libraries:
        required_version = required_libraries[lib]
        installed_version = pkg_resources.get_distribution(lib).version
        if pkg_resources.parse_version(installed_version) < pkg_resources.parse_version(
            required_version
        ):
            if not versions_mismatched_message:
                import_errors.append(
                    (
                        f"Required libraries version is incompatible "
                        "to use this feature."
                    )
                )
                versions_mismatched_message = True
            import_errors.append(
                (
                    f"  Please re-install {lib} with "
                    f"`pip install -I {lib}=={required_libraries[lib]}`."
                )
            )

if import_errors:
    raise ImportError("\n".join(import_errors))
from ansys.fluent.visualization._config import get_config, set_config  # noqa: F401
