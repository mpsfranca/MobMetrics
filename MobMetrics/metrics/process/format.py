# Related third party imports.
import pandas as pd


class Format:
    """
        Class responsable to pre process all dataframe
    """
    def __init__(self, trace):
        self.trace = trace

    def extract(self):
        """Processes and formats the input DataFrame."""
        if self.trace.empty:
            print("Trace is empty")

        self._create_id()

        # Convert 'time' column to datetime if it's a string
        if isinstance(self.trace.iloc[0]['time'], str):
            self._to_datetime()

        self._sort()
        self._create_z()

        return self.trace

    def _to_datetime(self):
        """Converts the 'time' column to datetime and renames it to 'date_time'."""
        self.trace['time'] = pd.to_datetime(self.trace['time'])
        self.trace = self.trace.rename(columns={'time': 'date_time'})
        self._date_to_float()

    def _date_to_float(self):
        """Transforms the 'date_time' column to relative time in seconds (float)."""
        self.trace = self.trace.sort_values(by=['date_time'])
        first_time = self.trace.iloc[0]['date_time']
        self.trace['time'] = (self.trace['date_time'] - first_time).dt.total_seconds()
        self.trace.loc[0, 'time'] = 0

    def _sort(self):
        """Sorts the DataFrame by 'id' and 'time'."""
        self.trace = self.trace.sort_values(by=['id', 'time'])

    def _create_z(self):
        """Adds a 'z' column with default value 0 if it does not exist."""
        if 'z' not in self.trace.columns:
            self.trace['z'] = 0

    def _create_id(self):
        """Adds an 'id' column with default value 1 if it does not exist."""
        if 'id' not in self.trace.columns:
            self.trace['id'] = 1