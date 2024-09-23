"""Abstract module providing plotter functionality."""

from abc import ABC, abstractmethod


class AbstractPlotter(ABC):
    """Abstract class for plotter."""

    @abstractmethod
    def plot(self, data: dict) -> None:
        """Draw plot in window.

        Parameters
        ----------
        data : dict
            Data to plot. Data consists the list of x and y
            values for each curve.
        """
        pass

    @abstractmethod
    def close(self):
        """Close plotter window."""
        pass

    @abstractmethod
    def is_closed(self):
        """Check if the plotter window is closed."""
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
    def set_properties(self, properties: dict):
        """Set plot properties.

        Parameters
        ----------
        properties : dict
            Plot properties i.e. curves, title, xlabel and ylabel.
        """
        pass
