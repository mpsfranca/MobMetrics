from abc import ABC, abstractmethod


class AbsData(ABC):
    """
    Abstract base class for defining data Analytics Methods.

    Subclasses must implement the `extract` method.
    """

    @abstractmethod
    def extract(self):
        """
        Abstract method to be implemented by subclasses.

        This method should define the logic for extracting the metric.
        """
        pass
