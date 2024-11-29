"""A wrapper to improve the user interface of graphics."""

from ansys.fluent.visualization.graphics import graphics_windows_manager


class GraphicsWindow:
    def __init__(self, grid: tuple = (1, 1)):
        self._grid = grid
        self._graphics_objs = []
        self.window_id = None

    def add_graphics(
        self,
        object,
        position: tuple = (0, 0),
        opacity: float = 1,
    ) -> None:
        """Add data to a plot.

        Parameters
        ----------
        object: GraphicsDefn
            Object to plot as a sub-plot.
        position: tuple, optional
            Position of the sub-plot.
        opacity: float, optional
            Transparency of the sub-plot.
        """
        self._graphics_objs.append({**locals()})

    def show(self) -> None:
        """Render the objects in window and display the same."""
        self.window_id = graphics_windows_manager.open_window(grid=self._grid)
        self.graphics_window = graphics_windows_manager._post_windows.get(
            self.window_id
        )
        self._renderer = self.graphics_window.renderer
        self.plotter = self.graphics_window.renderer.plotter
        for i in range(len(self._graphics_objs)):
            graphics_windows_manager.add_graphics(
                object=self._graphics_objs[i]["object"].obj,
                window_id=self.window_id,
                fetch_data=True,
                overlay=True,
                position=self._graphics_objs[i]["position"],
                opacity=self._graphics_objs[i]["opacity"],
            )
        graphics_windows_manager.show_graphics(self.window_id)

    def save_graphic(
        self,
        format: str,
    ) -> None:
        """Save a graphics.

        Parameters
        ----------
        format : str
            Graphic file format. Supported formats are SVG, EPS, PS, PDF, and TEX.

        Raises
        ------
        ValueError
            If the window does not support the specified format.
        """
        if self.window_id:
            self._renderer.save_graphic(f"{self.window_id}.{format}")

    def refresh_windows(
        self,
        session_id: str | None = "",
        overlay: bool | None = False,
    ) -> None:
        """Refresh windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for refreshing the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are refreshed.
        overlay : bool, Optional
            Overlay graphics over existing graphics.
        """
        if self.window_id:
            graphics_windows_manager.refresh_windows(
                windows_id=[self.window_id], session_id=session_id, overlay=overlay
            )

    def animate_windows(
        self,
        session_id: str | None = "",
    ) -> None:
        """Animate windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for animating the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are animated.

        Raises
        ------
        NotImplementedError
            If not implemented.
        """
        if self.window_id:
            graphics_windows_manager.animate_windows(
                windows_id=[self.window_id], session_id=session_id
            )

    def close_windows(
        self,
        session_id: str | None = "",
    ) -> None:
        """Close windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for closing the windows that belong only to this session.
           The default is ``""``, in which case the windows in all sessions
           are closed.
        """
        if self.window_id:
            graphics_windows_manager.close_windows(
                windows_id=[self.window_id], session_id=session_id
            )
