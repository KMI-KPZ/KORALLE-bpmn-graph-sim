import graph_structure

class Process:
    def __init__(self, graph, process_id, start_time=0.0):
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
