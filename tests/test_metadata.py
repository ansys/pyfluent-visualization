from ansys.fluent.visualization import __version__


def test_pkg_version():
    assert __version__ == "0.5.1"
