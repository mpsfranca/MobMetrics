import logging
from .utils import distance  # Function to calculate the distance between two points
from ...models import StayPointModel, VisitModel  # Django models for StayPoint and Visit

class StayPoints:
    """
    Class to calculate and save stay points and associated visits.
    """
    
    def __init__(self, trace, distance_threshold, time_threshold, entity_id, name):
        """
        Initializes the StayPoints class with the provided parameters.

        :param trace: DataFrame containing the dataset with the trajectory.
        :param distance_threshold: Distance threshold to consider nearby points.
        :param time_threshold: Time threshold to consider points as part of the same stay.
        :param entity_id: Unique identifier for the entity (user, vehicle, etc.).
        :param name: Name or identifier of the file associated with the trajectory.
        """
        self.trace = trace  # Trajectory data (as a DataFrame)
        self.distance_threshold = distance_threshold  # Distance threshold in meters
        self.time_threshold = time_threshold  # Time threshold in seconds
        self.entity_id = entity_id  # ID of the entity (e.g., user or vehicle)
        self.name = name  # File name associated with the trajectory

    def extract(self):
        """
        Extracts stay points from the trajectory and saves them to the database.

        For each stay point, a new visit is created in the VisitModel.
        Returns the updated DataFrame with the assigned spId for each point.
        """
        logging.info("Calculating Stay Points")  # Log the start of stay point calculation

        self.trace['spId'] = 0  # Initialize a new column for stay point IDs
        stay_point_id = 1  # Start with the first stay point ID
        m = 0  # Start processing trajectory data

        while m < len(self.trace):
            # Skip points that already have an assigned spId
            if self.trace.iloc[m]['spId'] != 0:
                m += 1
                continue

            # Variables to calculate the stay point
            arvT = self.trace.iloc[m]['time']  # Arrival time
            lat_sum = self.trace.iloc[m]['x']  # Sum of latitudes
            lgnt_sum = self.trace.iloc[m]['y']  # Sum of longitudes
            alt_sum = self.trace.iloc[m]['z']  # Sum of altitudes
            buffer = 1  # Buffer to count the number of points in the stay

            i = m + 1  # Start grouping points into the stay
            while i < len(self.trace) and distance(self.trace.iloc[m], self.trace.iloc[i]) <= self.distance_threshold:
                lat_sum += self.trace.iloc[i]['x']
                lgnt_sum += self.trace.iloc[i]['y']
                alt_sum += self.trace.iloc[i]['z']
                buffer += 1  # Increase the number of points in the stay
                i += 1

            levT = self.trace.iloc[i - 1]['time']  # Departure time (last point in the stay)

            # Check if the stay duration exceeds the time threshold
            if (levT - arvT) >= self.time_threshold:
                # Calculate the average coordinates of the stay
                x = round(lat_sum / buffer, 5)
                y = round(lgnt_sum / buffer, 5)
                z = round(alt_sum / buffer, 5)

                exists = True  # Flag to check if the stay point already exists
                # Check if a similar stay point already exists in the database
                for aux in StayPointModel.objects.filter(fileName=self.name):  # Filter by the associated file name
                    if distance({'x': aux.x, 'y': aux.y, 'z': aux.z}, {'x': x, 'y': y, 'z': z}) <= self.distance_threshold:
                        # If a similar point exists, update the spId for trajectory points
                        self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = aux.spId
                        aux.numVisits += 1  # Increment the number of visits
                        aux.save()  # Save the updated stay point

                        # Create a visit for the stay point
                        VisitModel.objects.create(
                            entityId=self.entity_id,
                            spId=aux.spId,
                            fileName=self.name,  # Save the file name
                            arvT=arvT,
                            levT=levT,
                            visitT=levT - arvT  # Duration of the visit
                        )
                        exists = False  # Stay point already exists
                        break

                if exists:
                    # If no similar stay point exists, create a new stay point
                    new_stay_point = StayPointModel.objects.create(
                        spId=stay_point_id,
                        x=x,
                        y=y,
                        z=z,
                        numVisits=1,  # This is the first visit to the stay point
                        fileName=self.name  # Associate the new stay point with the file name
                    )
                    # Assign the new spId to the trajectory points
                    self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = stay_point_id

                    # Create a visit for the new stay point
                    VisitModel.objects.create(
                        entityId=self.entity_id,
                        spId=stay_point_id,
                        fileName=self.name,  # Save the file name
                        arvT=arvT,
                        levT=levT,
                        visitT=levT - arvT  # Duration of the visit
                    )

                    stay_point_id += 1  # Increment the ID for the next stay point

            m = i  # Move to the next point in the trajectory

        logging.info("Stay Points Calculated Successfully")  # Log the end of stay point calculation
        return self.trace  # Return the updated DataFrame with assigned stay point IDs
