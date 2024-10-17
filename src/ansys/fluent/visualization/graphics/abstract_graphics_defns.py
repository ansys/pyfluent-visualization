"""Abstract module providing graphics functionality."""

from abc import ABC, abstractmethod


class AbstractRenderer(ABC):
    """Abstract class for renderer."""

    @abstractmethod
    def show(self):
        """Show graphics."""
        pass

    @abstractmethod
    def render(self, mesh, **kwargs):
        """Render graphics in window."""
        pass

    @abstractmethod
    def save_graphic(self, file_name: str):
        """Save graphics to the specified file.

        Parameters
        ----------
        file_name : str
            File name to save graphic.
        """
        pass

    @abstractmethod
    def get_animation(self, win_id: str):
        """Animate windows.

        Parameters
        ----------
        win_id : str
            ID for the window to animate.
        """
        pass

    @abstractmethod
    def close(self):
        """Close graphics window."""
        pass
