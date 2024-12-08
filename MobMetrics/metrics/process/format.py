import pandas as pd

class Format:
    def __init__(self, trace):
        self.trace = trace

    def extract(self):
        self.creat_id()
        if type(self.trace.iloc[0]['time']) == str:
            self.to_date_time()
        self.sort()
        self.creat_z()
        

        return self.trace

    def to_date_time(self):
        self.trace['time'] = pd.to_datetime(self.trace['time'])
        self.trace = self.trace.rename(columns={'time': 'date_time'})
        self.date_to_float()

    def date_to_float(self):
        self.trace = self.trace.sort_values(by=['date_time'])
        first_time = self.trace.iloc[0]['date_time']
        self.trace['time'] = (self.trace['date_time'] - first_time).dt.total_seconds()
        self.trace.loc[0, 'time'] = 0

    def sort(self):
        self.trace = self.trace.sort_values(by=['id', 'time'])

    def creat_z(self):
        if 'z' in self.trace.columns:
            pass
        else:
            self.trace['z'] = 0
    
    def creat_id(self):
        if 'id' in self.trace.columns:
            pass
        else:
            self.trace['id'] = 1