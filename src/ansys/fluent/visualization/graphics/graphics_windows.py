from ansys.fluent.visualization.graphics import graphics_windows_manager


class GraphicsWrapper:
    def __init__(self):
        self.window_id = graphics_windows_manager.open_window()
        self.graphics_window = graphics_windows_manager._post_windows.get(
            self.window_id
        )
        self.renderer = self.graphics_window.renderer
        self.plotter = self.graphics_window.renderer.plotter

    def plot(
        self, object, fetch_data: bool | None = False, overlay: bool | None = False
    ) -> None:
        """Draw a plot.

        Parameters
        ----------
        object: GraphicsDefn
            Object to plot.
        fetch_data : bool|None
            Whether to fetch data. The default is ``False``.
        overlay : bool|None
            Whether to overlay graphics over existing graphics.
            The default is ``False``.
        """
        graphics_windows_manager.plot(
            object=object,
            window_id=self.window_id,
            fetch_data=fetch_data,
            overlay=overlay,
        )

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
        self.graphics_window.renderer.save_graphic(f"{self.window_id}.{format}")

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
        graphics_windows_manager.close_windows(
            windows_id=[self.window_id], session_id=session_id
        )
