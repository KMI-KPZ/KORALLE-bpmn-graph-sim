import numpy as np # We need numpy for the normal random variables

class Node:
    '''
    A class to represent the node of a graph

    Attributes:
        name : str
            Name of the node
        id : str
            ID of the node (from BPMN file)
        sample_time : float
            Average time for the node to run in the simulation
        sample_variance : float
            Variance for the average for the node to run in the simulation
        capacity : int
            How many processes may run this node in unison
        fail_chance : float
            The chance for this node to fail, causing it to restart
        gateway_type : str
            Defines the behaviour of the node when it finishes
        given_time : float
            The time given for the node:
            given_time ~ Normal(sample_time, sqrt(sample_variance))
    '''

    def __init__(self, 
                 name,
                 node_id,
                 sample_time,
                 sample_variance,
                 capacity, 
                 fail_chance,
                 gateway_type
                 ):
        '''
        Constructs the necessary attributes for the Node object
        
            Parameters:
                see Node.__doc__ under "attributes"
        '''

        self.name = name
        self.id = node_id
        self.sample_time = sample_time
        self.sample_variance = sample_variance
        self.capacity = capacity
        self.fail_chance = fail_chance
        self.gateway_type = gateway_type
        self.given_time = sample_time

        self.outgoing = []
        self.incoming = []
        
class Graph:
    '''
    A class to represent a DIRECTED GRAPH which holds data on the process
    within a BPMN file

    Attributes:
        nodes : dict[str, Node]
            A dictionary of each node within the graph indexed by its ID
        start : Node
            A node which the simulation will start at
        end : Node
            The node representing the end of the simulation
        time_spent_waiting : float
            The amount of time (in time steps) which was wasted due to
            blockages in the process

    Methods:
        reset_time_lefts():
            Resets the given_time for every node in the graph
        add_node(node):
            Adds a Node object to the nodes dictionary
        add_edge(a, b):
            Adds an edge between node a and node b
        get_node(node_id):
            Returns the node object which the given node ID
    '''

    def __init__(self):
        '''
        Constructs the necessary attributes for the Graph object.
        Also randomises the given_time of each node.
        '''
        self.nodes = {}
        self.start: Node | None = None
        self.end: Node | None = None

        self.time_spent_waiting = 0.0
        self.reset_time_lefts()

    def reset_time_lefts(self, randomise=True):
        '''
        Resets the given_time of each node in the graph

            Parameters:
                randomise : bool
                    If true, the given_time will be randomised according to a normal
                    ditribution. If not, the exact time will be equal to sample_time.
        '''

        for node in self.nodes.values():
            # Randomise the time given according to mean and variance given,
            # and ensure it isn't negative
            if randomise:
                node.given_time = max(0, 
                            np.random.normal(node.sample_time, np.sqrt(node.sample_variance))
                            )
                        
            else:
                node.given_time = node.sample_time

    def add_node(self, node: Node):
        '''
        Adds a node to the graph

            Parameters:
                node : Node
                    The Node object to add
        '''

        self.nodes[node.id] = node

    def add_edge(self, a: Node, b: Node):
        '''
        Adds an edge between the two given nodes by appending each other to their
        outgoing and incoming lists, respectively

            Parameters:
                a : Node
                b : Node
                    The nodes through which edge runs in the direction from a to b
        '''

        a.outgoing.append(b)
        b.incoming.append(a)

    def get_node(self, node_id: str):
        '''
        Returns the node in the graph with the specified ID

            Parameters:
                node_id : str
                    The node ID to search for
        '''

        # TODO
        # This method SHOULD be used in some spots in the code (graph_simulation.py most likely)
        # but isn't. This would make the code more readable if it is consistant.

        return self.nodes[node_id]



