import xml.etree.ElementTree as ET
from pathlib import Path

import graph_structure as gs

def check_file(file_name):
    '''
    Raises an error ifthe given file name is not a .BPMN file
        
        Parameters:
            file_name : str
                The name of the file within the project root folder
    '''

    path = Path(file_name)

    if path.suffix != ".bpmn":
        raise ValueError("file must end with .bpmn")

    if not path.is_file():
        raise ValueError("file not found")

class BpmnFile:
    '''
    A class to represent a BPMN File

    Attributes:
        process : ET.Element
            BPMN process object
        tree : ET.ElementTree
            Full BPMN tree represented as a ElementTree object
        root:  ET.Element
            The root object in the BPMN, i.e. <definitions>

    Methods:
        get_graph_structure():
            Returns a graph_structure.Graph object represnting the BPMN file
    '''

    def __init__(self, file_name):
        '''
        Constructs the necessary attributes for the BpmnFile object

            Parameters:
                file_name : str
                    The name of the file within the project root folder
        '''

        # raise an error if the file is invalid
        check_file(file_name)
        
        # tree is a ElementTree object which makes it easy to read the xml file
        parser = ET.XMLParser(encoding="utf-8")
        tree = ET.parse(file_name, parser=parser)
        
        if tree is None:
            raise Exception("no tree found in bpmn file")

        # root represents the <definitions/> object for a BPMN file
        root = tree.getroot()

        # we need the BPMN namespace in order to get the object names and types
        if root.tag.startswith("{"):
            namespace = root.tag[root.tag.find("{") + 1 : root.tag.find("}")]
        else:
            raise Exception("no namespace found in BPMN file")

        ns = {"bpmn" : namespace}
        process = root.find("bpmn:process", ns)

        if process is None:
            raise Exception("no process element found in bpmn")
        
        # set the attributes needed to create a Graph object
        self.process = process
        self.tree = tree
        self.root = root

    def get_graph_structure(self):
        '''
        Returns a Graph object represnting the BPMN file including the start and end nodes.
        '''

        graph = gs.Graph()

        for child in self.process:
            # we want to ignore the edges for now
            if child.tag.endswith("sequenceFlow"):
                continue
            
            # all data is kept in the name (see README or a few lines down)
            node_data = child.get("name")

            # parsing the data into seperate variables
            if node_data:
                try:
                    name, time, variance, capacity, fail_chance, gatetype = node_data.split(";")
                    time = float(time)
                    variance = float(variance)
                    capacity = int(capacity)
                    fail_chance = float(fail_chance)
                    gatetype = str(gatetype)
                except ValueError:
                    raise ValueError(f'Invalid task format: "{node_data}". Expected "name;time;variance;capacity;failchance;gatetype"')
            else: # a node has no space in the BPMN for name, it will default to these values
                name = child.tag.split("}")[-1]
                time = 0.0
                variance = 0.0
                capacity = 99999999 # hopefully no one tries to run n=10000000
                fail_chance = 0.0
                gatetype = "AND"

            _validate_values(time, variance, capacity, fail_chance, gatetype)

            # We need to make sure the start event and end event are handled carefully
            node_id = child.get("id") or ""

            node_to_add = gs.Node(
                         name,
                         node_id,
                         time,
                         variance,
                         capacity, 
                         fail_chance,
                         gatetype)

            if child.tag.endswith("startEvent"):
                node_to_add.capacity = 99999999
                node_to_add.sample_time = 0
                node_to_add.given_time = 0
                node_to_add.sample_variance = 0
                node_to_add.gateway_type = "AND"
                graph.start = node_to_add 
            elif child.tag.endswith("endEvent"):
                node_to_add.capacity = 99999999
                node_to_add.sample_time = 0
                node_to_add.given_time = 0
                node_to_add.sample_variance = 0
                node_to_add.gateway_type = "AND"
                graph.end = node_to_add
 
            graph.add_node(node_to_add)
           
        # We may now handle the edges in the graph
        for child in self.process:
            if not child.tag.endswith("sequenceFlow"):
                continue
            
            source_node = graph.nodes[child.get("sourceRef")]
            target_node = graph.nodes[child.get("targetRef")]

            if source_node is None or target_node is None:
                raise Exception("sequenceFlow references an unknown node")
            
            graph.add_edge(source_node, target_node)

        return graph

def _validate_values(time, variance, capacity, fail_chance, gatetype):
    '''
    Validates the values within a single BPMN Task to ensure they don't cause errors later.
    If a value is not possible, an error is raised.

        Parameters:
            time : float
                The time for a BPMN task, hence must be positive
            variance : float
                The variance in time for a BPMN task, hence must be positive
            capacity : int
                The number of processes which can run the this node at the same time
            fail_chance : float
                The chance for a task to fail and have to restart
            gatetype : str
                Defines the behaviour which should occur when the task ends
    '''

    # time must be >= 0
    if time < 0:
        raise ValueError("BPMN Node time value must be greater than or equal to 0")
    
    # variance must be >= 0
    if variance < 0:
        raise ValueError("BPMN Node variance must be greater than or equal to 0")
    
    # capacity must be > 0
    if capacity <= 0:
        raise ValueError("BPMN Node capacity must be a positive integer")

    # fail_chance must be in [0,1]
    if not (0 <= fail_chance <= 1):
        raise ValueError("BPMN Node fail chance must be in the range [0,1]")

    # gatetype must be either AND, OR, or XOR
    if gatetype.lower() not in ["and", "or", "xor"]:
        raise ValueError("BPMN Node gateway type must be either 'and', 'or', or 'xor'")


