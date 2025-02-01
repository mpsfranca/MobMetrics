from ..utils.utils import distance
from ..utils.abs_metric import AbsMetric

class TravelDistance(AbsMetric):
    def __init__(self, traces):
        """
        Initializes with the traces of the trip.
        :param traces: Iterable containing the travel points, each with 'x', 'y', and 'z' attributes.
        """
        self.traces = traces

    def extract(self):
        """
        Calculates the total distance traveled between trace points.
        :return: Total distance traveled as a float.
        """
        distancia_total = 0

        # Ensure traces are iterable and have at least two points
        if len(self.traces) < 2:
            return distancia_total

        # Initialize the previous trace as the first point
        previous_trace = self.traces.iloc[0]  # For DataFrame, use .iloc for row access

        # Iterate over the traces starting from the second point
        for i in range(1, len(self.traces)):
            current_trace = self.traces.iloc[i]  # Access current trace

            # Convert points to dictionary format expected by the `distance` function
            first_point = {'x': previous_trace['x'], 'y': previous_trace['y'], 'z': previous_trace['z']}
            second_point = {'x': current_trace['x'], 'y': current_trace['y'], 'z': current_trace['z']}

            # Add the distance between the two points
            distancia_total += distance(first_point, second_point)

            # Update the previous trace
            previous_trace = current_trace

        return distancia_total
