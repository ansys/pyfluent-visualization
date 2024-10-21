from ansys.fluent.visualization.plotter import plotter_windows_manager


class PlotterWrapper:
    def __init__(self):
        self.window_id = plotter_windows_manager.open_window()
        self.plotter_window = plotter_windows_manager._post_windows.get(self.window_id)
        self.plotter = self.plotter_window.plotter

    def plot(self, object) -> None:
        """Draw a plot.

        Parameters
        ----------
        object: PlotDefn
            Object to plot.
        """
        plotter_windows_manager.plot(
            object=object,
            window_id=self.window_id,
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
        self.plotter_window.plotter.save_graphic(f"{self.window_id}.{format}")

    def refresh_windows(
        self,
        session_id: str | None = "",
    ) -> None:
        """Refresh windows.

        Parameters
        ----------
        session_id : str, optional
           Session ID for refreshing the windows that belong only to this
           session. The default is ``""``, in which case the windows in all
           sessions are refreshed.
        """
        plotter_windows_manager.refresh_windows(
            windows_id=[self.window_id], session_id=session_id
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
        plotter_windows_manager.animate_windows(
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
        plotter_windows_manager.close_windows(
            windows_id=[self.window_id], session_id=session_id
        )
