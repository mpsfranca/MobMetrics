from ..utils.utils import distance
from ...models import TraceModel, ContactModel

class DetectContact:
    def __init__(self, parameters, name):
        self.parameters = parameters
        self.name = name

    def extract(self):
        trace = TraceModel.objects.filter(fileName=self.name).order_by('time')
        contacts = []

        # A dictionary to track ongoing contacts
        ongoing_contacts = {}

        for aux in trace:
            for aux_2 in trace:
                if aux.time == aux_2.time and aux.entityId != aux_2.entityId:
                    dist = distance(
                        {'x': aux.x, 'y': aux.y, 'z': aux.z},
                        {'x': aux_2.x, 'y': aux_2.y, 'z': aux_2.z}
                    )
                    
                    # Unique contact identifier
                    contact_key = (aux.entityId, aux_2.entityId)

                    if dist <= self.parameters[2]:
                        if contact_key not in ongoing_contacts:
                            # Start a new contact
                            ongoing_contacts[contact_key] = {
                                'id1': aux.entityId,
                                'id2': aux_2.entityId,
                                'start_time': aux.time,
                                'start_x_id_1': aux.x,
                                'start_y_id_1': aux.y,
                                'start_z_id_1': aux.z,
                                'start_x_id_2': aux_2.x,
                                'start_y_id_2': aux_2.y,
                                'start_z_id_2': aux_2.z,
                                'end_time': aux.time
                            }
                        else:
                            # Update the end time of the ongoing contact
                            ongoing_contacts[contact_key]['end_time'] = aux.time
                    else:
                        if contact_key in ongoing_contacts:
                            # End the contact
                            contact = ongoing_contacts.pop(contact_key)
                            contact.update({
                                'end_x_id_1': aux.x,
                                'end_y_id_1': aux.y,
                                'end_z_id_1': aux.z,
                                'end_x_id_2': aux_2.x,
                                'end_y_id_2': aux_2.y,
                                'end_z_id_2': aux_2.z
                            })
                            contacts.append(contact)

        # Add remaining ongoing contacts
        for contact in ongoing_contacts.values():
            contacts.append(contact)

        # Bulk save detected contacts to the database
        ContactModel.objects.bulk_create([
            ContactModel(
                fileName=self.name,
                id1=c['id1'],
                id2=c['id2'],
                start_time=c['start_time'],
                end_time=c['end_time'],
                start_x_id_1=c['start_x_id_1'],
                start_x_id_2=c['start_x_id_2'],
                start_y_id_1=c['start_y_id_1'],
                start_y_id_2=c['start_y_id_2'],
                start_z_id_1=c['start_z_id_1'],
                start_z_id_2=c['start_z_id_2'],
                end_x_id_1=c.get('end_x_id_1'),
                end_x_id_2=c.get('end_x_id_2'),
                end_y_id_1=c.get('end_y_id_1'),
                end_y_id_2=c.get('end_y_id_2'),
                end_z_id_1=c.get('end_z_id_1'),
                end_z_id_2=c.get('end_z_id_2')
            ) for c in contacts
        ])
