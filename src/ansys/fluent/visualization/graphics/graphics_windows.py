"""A wrapper to improve the user interface of graphics."""

import os

from ansys.fluent.visualization import get_config
from ansys.fluent.visualization.graphics import graphics_windows_manager
from ansys.fluent.visualization.plotter.plotter_windows import PlotterWindow


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
        title: str = "",
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
        title: str, optional
            Title of the sub-plot (only for plots).
        """
        self._graphics_objs.append({**locals()})

    def _all_plt_objs(self):
        from ansys.fluent.core.post_objects.post_object_definitions import PlotDefn

        for obj in self._graphics_objs:
            if not isinstance(obj["object"].obj, PlotDefn):
                return False
        return True

    @staticmethod
    def _display_graphics(session, type_str: str, obj_name: str):
        session.scheme_eval.scheme_eval(
            f"(define temp-obj (get-temporary-graphics-object '{type_str}))"
        )
        session.scheme_eval.scheme_eval(
            f"(define temp (send graphics-manager copy-from-object "
            f'"{obj_name}" temp-obj))'
        )
        session.scheme_eval.scheme_eval(
            f"""(send temp-obj set-var! 'name "{obj_name}")"""
        )
        session.scheme_eval.scheme_eval(
            "(send graphics-manager display-object (send temp-obj get-var 'name))"
        )

    def _show_interactive(self):
        for graphics_obj in self._graphics_objs:
            post_obj = graphics_obj["object"].obj
            if post_obj.__class__.__name__ == "Mesh":
                post_obj.session.results.graphics.mesh[post_obj._name] = {
                    "surfaces_list": post_obj.surfaces(),
                    "options": {
                        "nodes": post_obj.show_nodes(),
                        "edges": post_obj.show_edges(),
                        "faces": post_obj.show_faces(),
                    },
                }
                post_obj.session.settings.results.graphics.windows.open_window()
                self._display_graphics(post_obj.session, "mesh", post_obj._name)
                del post_obj.session.results.graphics.mesh[post_obj._name]
            elif post_obj.__class__.__name__ == "Surface":
                if post_obj.definition.type() == "plane-surface":
                    plane_surf = post_obj.definition.plane_surface
                    post_obj.session.results.surfaces.plane_surface[post_obj._name] = {
                        "method": plane_surf.creation_method(),
                        list(
                            plane_surf()[
                                plane_surf.creation_method().replace("-", "_")
                            ].keys()
                        )[0]: list(
                            plane_surf()[
                                plane_surf.creation_method().replace("-", "_")
                            ].values()
                        )[
                            0
                        ],
                    }
                    post_obj.session.settings.results.graphics.windows.open_window()
                    post_obj.session.results.surfaces.plane_surface[
                        post_obj._name
                    ].display()
                else:
                    post_obj.session.results.surfaces.iso_surface[post_obj._name] = {
                        "field": post_obj.definition.iso_surface.field(),
                        "iso_values": [post_obj.definition.iso_surface.iso_value()],
                    }
                    post_obj.session.settings.results.graphics.windows.open_window()
                    if post_obj.definition.iso_surface.rendering() == "contour":
                        post_obj.session.results.graphics.contour[post_obj._name] = {
                            "field": post_obj.definition.iso_surface.field(),
                            "surfaces_list": [post_obj._name],
                        }
                        self._display_graphics(
                            post_obj.session, "contour", post_obj._name
                        )
                        del post_obj.session.results.graphics.contour[post_obj._name]
                    else:
                        post_obj.session.results.surfaces.iso_surface[
                            post_obj._name
                        ].display()
            elif post_obj.__class__.__name__ == "Contour":
                post_obj.session.results.graphics.contour[post_obj._name] = {
                    "field": post_obj.field(),
                    "surfaces_list": post_obj.surfaces(),
                    "filled": post_obj.filled(),
                    "node_values": post_obj.node_values(),
                    "boundary_values": post_obj.boundary_values(),
                    "contour_lines": post_obj.contour_lines(),
                }
                post_obj.session.results.graphics.contour[
                    post_obj._name
                ].range_option.set_state(post_obj.range())
                post_obj.session.settings.results.graphics.windows.open_window()
                self._display_graphics(post_obj.session, "contour", post_obj._name)
                del post_obj.session.results.graphics.contour[post_obj._name]
            elif post_obj.__class__.__name__ == "Vector":
                post_obj.session.results.graphics.vector[post_obj._name] = {
                    "vector_field": post_obj.vectors_of(),
                    "field": post_obj.field(),
                    "surfaces_list": post_obj.surfaces(),
                    "skip": post_obj.skip(),
                }
                post_obj.session.results.graphics.vector[
                    post_obj._name
                ].scale.scale_f = post_obj.scale()
                post_obj.session.results.graphics.vector[
                    post_obj._name
                ].range_option.set_state(post_obj.range())
                post_obj.session.settings.results.graphics.windows.open_window()
                self._display_graphics(post_obj.session, "vector", post_obj._name)
                del post_obj.session.results.graphics.vector[post_obj._name]
            elif post_obj.__class__.__name__ == "Pathlines":
                post_obj.session.results.graphics.pathline[post_obj._name] = {
                    "field": post_obj.field(),
                    "release_from_surfaces": post_obj.surfaces(),
                }
                post_obj.session.settings.results.graphics.windows.open_window()
                self._display_graphics(post_obj.session, "pathlines", post_obj._name)
                del post_obj.session.results.graphics.pathline[post_obj._name]
            elif post_obj.__class__.__name__ == "XYPlot":
                post_obj.session.results.plot.xy_plot[post_obj._name] = {
                    "surfaces_list": post_obj.surfaces(),
                    "axes": {
                        "labels": {
                            "x_axis": post_obj.x_axis_function(),
                            "y_axis": post_obj.y_axis_function(),
                        }
                    },
                    "plot_direction": {
                        "direction_vector": {
                            "x_component": post_obj.direction_vector()[0],
                            "y_component": post_obj.direction_vector()[1],
                            "z_component": post_obj.direction_vector()[2],
                        }
                    },
                }
                post_obj.session.settings.results.graphics.windows.open_window()
                self._display_graphics(post_obj.session, "xy-plot", post_obj._name)
                del post_obj.session.results.plot.xy_plot[post_obj._name]
            elif post_obj.__class__.__name__ == "MonitorPlot":
                post_obj.session.solution.monitor.residual.plot()
            else:
                raise RuntimeError("Wrong choice.")

    def show(self) -> None:
        """Render the objects in window and display the same."""
        import ansys.fluent.visualization as pyviz

        if os.getenv("FLUENT_PROD_DIR") and pyviz.INTERACTIVE:
            self._show_interactive()
        else:
            self.window_id = graphics_windows_manager.open_window(grid=self._grid)
            if self._all_plt_objs() and get_config()["blocking"]:
                p = PlotterWindow(grid=self._grid)
                for obj in self._graphics_objs:
                    p.add_plots(
                        obj["object"], position=obj["position"], title=obj["title"]
                    )
                p.show(self.window_id)
            else:
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
