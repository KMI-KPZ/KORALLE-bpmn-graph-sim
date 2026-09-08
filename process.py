import graph_structure

class Process:
    '''
    A class to represent a single process within a simulation.

    Attributes:
        graph : graph_structure.Graph
            The graph object made from the BPMN file
        process_id : any (made to be int, though)
            The process ID
        current_running_nodes : dict[Node, float]
            A dictionary of all nodes which the process is actively occupying
            Updates with time
        start_time : float
            The time (in time steps) when the process began
        end_time : float
            The time (in time steps) when the process ended
        finished : bool
            Becomes True if the process reaches a halt (False otherwise)
        time_waiting : float
            The time the process spent waiting for nodes to be finished in
            order to move on
        possibly_stuck : bool
            False until the process reaches a position where the only
            node in current_running_nodes is NOT the end node AND has
            no outgoing nodes, i.e. the process is stuck at some terminal node
            with no way to reach the end node
    '''

    def __init__(self, graph, process_id, start_time=0.0):
        '''
        Constructs the necessary attributes for the Process object
        '''

        self.graph = graph
        self.process_id = process_id

        self.current_running_nodes = {
            self.graph.start: self.graph.start.given_time
        }

        self.start_time = start_time
        self.end_time = None

        self.finished = False
        self.time_waiting = 0
        self.possibly_stuck = False
