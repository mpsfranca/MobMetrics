# Related third party imports.
from tqdm import tqdm

# Local application/library specific imports.
from ..utils.utils import distance
from ...models import ContactModel


class DetectContact:
    """
    Class responsible for detecting physical contacts between entities based on spatial distance
    at each timestamp.

    Attributes:
        parameters (list): Configuration parameters used to guide the contact detection.
        trace (DataFrame): Trajectory data containing positions and timestamps.
    """

    def __init__(self, parameters, trace):
        """
        Initialize the DetectContact class.

        Args:
            parameters (list): Configuration parameters.
            trace (DataFrame): Data containing positions, timestamps, and entity IDs.
        """
        self.parameters = parameters
        self.trace = trace

    def extract(self):
        """
        Main method that iterates over all timestamps and checks for proximity-based contact
        between each pair of entities.
        """
        unique_times = self.trace['time'].unique()

        for t in tqdm(unique_times, desc="Processing contacts"):
            subset = self.trace[self.trace['time'] == t]

            if len(subset) < 2:
                continue

            objects = subset.to_dict(orient='records')

            for i in range(len(objects)):
                for j in range(i + 1, len(objects)):
                    obj1, obj2 = objects[i], objects[j]

                    dist = distance(obj1, obj2, self.parameters[6])

                    if dist < self.parameters[2]:
                        contact = ContactModel(
                            file_name=self.parameters[4],
                            id1 = obj1['id'],
                            id2 = obj2['id'],
                            contact_timestamp = t,
                            x_id1 = obj1['x'],
                            x_id2 = obj2['x'],
                            y_id1 = obj1['y'],
                            y_id2 = obj2['y'],
                            z_id1 = obj1['z'],
                            z_id2 = obj2['z'],
                        )
                        contact.save()
