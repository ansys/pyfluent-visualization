from ansys.fluent.visualization.plotter import plotter_windows_manager


class PlotterWindow:
    def __init__(self, grid: tuple = (1, 1)):
        self._grid = grid
        self._plot_objs = []
        self._subplot_titles = []
        self.window_id = None

    def add_plots(self, object, position: tuple = (0, 0), title: str = "") -> None:
        """Add data to a plot.

        Parameters
        ----------
        object: GraphicsDefn
            Object to plot as a sub-plot.
        position: tuple, optional
            Position of the sub-plot.
        title: str, optional
            Title of the sub-plot.
        """
        self._plot_objs.append({**locals()})
        if title:
            self._subplot_titles.append(title)
        elif hasattr(object.obj, "monitor_set_name"):
            self._subplot_titles.append(object.obj.monitor_set_name())
        else:
            self._subplot_titles.append("XYPlot")

    def show(self) -> None:
        """Render the objects in window and display the same."""
        self.window_id = plotter_windows_manager.open_window()
        self.plotter_window = plotter_windows_manager._post_windows.get(self.window_id)
        self.plotter = self.plotter_window.plotter
        for i in range(len(self._plot_objs)):
            plotter_windows_manager.plot(
                object=self._plot_objs[i]["object"].obj,
                window_id=self.window_id,
                grid=self._grid,
                position=self._plot_objs[i]["position"],
                subplot_titles=self._subplot_titles,
                show=False,
            )
        plotter_windows_manager.show_plots(window_id=self.window_id)

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
        if self.window_id:
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
        if self.window_id:
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
        if self.window_id:
            plotter_windows_manager.close_windows(
                windows_id=[self.window_id], session_id=session_id
            )
