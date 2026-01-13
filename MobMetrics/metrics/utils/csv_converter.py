from django.conf import settings

class Node:
    _instances = 0

    def __init__(self):
        self._positions = []
        self._id = Node._instances
        Node._instances += 1

    def addPosition(self,nodePosition):
        self._positions.append(nodePosition)

    def getPositions(self):
        return self._positions

    def __repr__(self):
        return f"Node {self._id}\nPositions: {self._positions}"
    
    def __eq__(self, other):
        return self._id == other._id

class NodePosition:
    def __init__(self,time,x,y):
        self._time = time
        self._x = x
        self._y = y

    def __repr__(self):
        return f"Time: {self._time}\nX Coordinate: {self._x}\nY Coordinate: {self._y}"


nodes = {}

def nodePopulate(scenario_name):
    with open(f"{settings.AUX_PATH}/{scenario_name}.csv","r") as bm:
        for line in bm:
            splitted_line = line.rstrip("\n")
            splitted_line = splitted_line.split(" ")
            current_node_id = splitted_line[0]
            current_node_time = splitted_line[1]
            current_node_x = splitted_line[2]
            current_node_y = splitted_line[3]
            current_node_position = NodePosition(current_node_time,current_node_x,current_node_y)
            if current_node_id not in nodes:
                node = Node()
                nodes[current_node_id] = node
            nodes[current_node_id].addPosition(current_node_position)

def csvWrite(name):
    with open(f"{settings.AUX_PATH}/{name}.csv", "w") as fcsv:
        fcsv.write("time,x,y,id\n")
        for key in nodes.keys():
            positions = nodes[key].getPositions()
            for position in positions:
                fcsv.write(f"{position._time},{position._x},{position._y},{nodes[key]._id}\n")
