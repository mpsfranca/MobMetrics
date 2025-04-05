from tqdm import tqdm

from ..utils.utils import distance  
from ...models import ContactModel 

class DetectContact:
    def __init__(self, parameters, trace):
        self.parameters = parameters      
        self.trace = trace 

    def extract(self):
        unique_times = self.trace['time'].unique()
        
        for t in tqdm(unique_times, desc="Processing contacts"):
            subset = self.trace[self.trace['time'] == t]
            
            if len(subset) < 2:
                continue
            
            objects = subset.to_dict(orient='records')
            
            for i in range(len(objects)):
                for j in range(i + 1, len(objects)):
                    obj1, obj2 = objects[i], objects[j]
                    
                    dist = distance(obj1, obj2)
                    
                    if dist < self.parameters[2]:
                        contact = ContactModel(
                            fileName=self.parameters[4],
                            id1=obj1['id'],
                            id2=obj2['id'],
                            contact_timestamp=t,
                            x_id_1=obj1['x'],
                            x_id_2=obj2['x'],
                            y_id_1=obj1['y'],
                            y_id_2=obj2['y'],
                            z_id_1=obj1['z'],
                            z_id_2=obj2['z'],
                        )
                        contact.save()
