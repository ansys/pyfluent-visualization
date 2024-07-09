"""Global configuration state for visualization."""

_global_config = {"blocking": False, "set_view_on_display": None}


def get_config() -> dict:
    """Retrieve visualization configuration.

    Returns
    -------
    config : dict
        Keys are parameter names that can be passed to :func:`set_config`.
    """
    return _global_config.copy()


def set_config(blocking: bool = True, set_view_on_display: str = None):
    """Set visualization configuration.

    Parameters
    ----------
    blocking : bool, default=False
        If True, then graphics/plot display will block the current thread.
    set_view_on_display : str, default=None
        If specified, then graphics will always be displayed in the specified view.
        Valid values are xy, xz, yx, yz, zx, zy and isometric.
    """
    if set_view_on_display not in set_config.allowed_views:
        raise ValueError(
            f"'{set_view_on_display}' is not an allowed view.\n"
            f"Allowed views are: {set_config.allowed_views}"
        )

    _global_config["blocking"] = blocking
    _global_config["set_view_on_display"] = set_view_on_display


set_config.allowed_views = ["xy", "xz", "yx", "yz", "zx", "zy", "isometric"]
