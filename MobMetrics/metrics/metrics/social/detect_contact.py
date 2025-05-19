# Standard library imports.
from typing import List

# Related third party imports.
import pandas as pd
from tqdm import tqdm

# Local application/library specific imports.
from ..utils.utils import distance
from ..utils.abs_metric import AbsMetric
from ...models import ContactModel, MetricsModel


class DetectContact(AbsMetric):
    """
    Class responsible for detecting physical contacts between entities based on spatial distance
    at each timestamp.
    
    Attributes:
        parameters (list): Configuration parameters used to guide the contact detection.
        trace (DataFrame): Trajectory data containing positions and timestamps.
    """

    def __init__(self, parameters: List, trace: pd.DataFrame):
        """
        Initialize the DetectContact class.

        Args:
            parameters (list): Configuration parameters.
            trace (DataFrame): Data containing positions, timestamps, and entity IDs.
        """
        self.parameters = parameters
        self.contact_time_threshold = parameters[7]
        self.file_name = parameters[4]
        self.trace = trace
        self.contacts = []

    def extract(self):
        self._find_contacts()
        self._find_continuite()
        self._contact_metrics()

    def _find_contacts(self):
        """
        Iterates over all timestamps and checks for proximity-based contact
        between each pair of entities.

        Returns:
            DataFrame: A pandas DataFrame containing the detected contacts.
        """
        unique_times = self.trace['time'].unique()
        contact_records = []

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
                        contact_records.append({
                            'file_name': self.parameters[4],
                            'id1': obj1['id'],
                            'id2': obj2['id'],
                            'contact_timestamp': t,
                        })
        
        self.contacts = pd.DataFrame(contact_records)


    def _find_continuite(self):
        """
        Finds and saves continuous contact periods between the same pair of entities.
        """
        if self.contacts.empty:
            raise ValueError("No contacts found. Run _find_contacts() first.")

        # Sort for proper sequential analysis
        self.contacts.sort_values(by=['id1', 'id2', 'contact_timestamp'], inplace=True)

        contact_instances = []
        prev_row = None
        start_timestamp = end_timestamp = None

        for _, row in self.contacts.iterrows():
            if (
                prev_row is not None and
                row['id1'] == prev_row['id1'] and
                row['id2'] == prev_row['id2'] and
                (row['contact_timestamp'] - prev_row['contact_timestamp']) <= self.contact_time_threshold
            ):
                # Extend the ongoing contact
                end_timestamp = row['contact_timestamp']
            else:
                # Save the previous contact if one was ongoing
                if prev_row is not None:
                    contact_instances.append(ContactModel(
                        file_name=self.file_name,
                        id1=prev_row['id1'],
                        id2=prev_row['id2'],
                        initial_timestamp=start_timestamp,
                        final_timestamp=end_timestamp,
                        contact_time=end_timestamp - start_timestamp
                    ))
                # Start a new contact
                start_timestamp = row['contact_timestamp']
                end_timestamp = row['contact_timestamp']

            prev_row = row

        # Save the last contact if needed
        if prev_row is not None:
            contact_instances.append(ContactModel(
                file_name=self.file_name,
                id1=prev_row['id1'],
                id2=prev_row['id2'],
                initial_timestamp=start_timestamp,
                final_timestamp=end_timestamp,
                contact_time=end_timestamp - start_timestamp
            ))

        # Save all contacts to the database at once
        ContactModel.objects.bulk_create(contact_instances)


    def _contact_metrics(self):

        contacts = ContactModel.objects.filter(file_name = self.file_name)

        for contact in contacts:
            id1 = contact.id1
            id2 = contact.id2
            contact_time = contact.contact_time

            ids = (id1, id2)

            for n in ids:

                metric = MetricsModel.objects.filter(file_name = self.file_name, entity_id = n).first()

                metric_total_contact_time = (metric.total_contact_time or 0) + contact_time
                metric_num_contacts = (metric.num_contacts or 0) + 1
                metric_avg_contact_time = metric_total_contact_time / metric_num_contacts


                metric.total_contact_time = metric_total_contact_time
                metric.num_contacts = metric_num_contacts
                metric.avg_contact_time = metric_avg_contact_time
                
                metric.save()


