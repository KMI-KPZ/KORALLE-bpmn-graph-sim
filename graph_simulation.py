# By Python standards, standard packages should be imported first, and then local files
import random
from copy import deepcopy
from time import sleep
from collections import defaultdict

import bpmn_parser
import process

class Simulation():
    '''
    A class to represent the state of a Graph Simulation.

    Attributes:
        graph : graph_structure.Graph
            Graph object representing the BPMN file
        timescale : float
            Speed multiplier of the simulation (for when the visualisation exists), default 1.0
        time_step_length : float
            The length of each step in time, default 1.0
        number_processes : int
            How many processes to run in the simulation, default 1
        stagger : float
            How much time to wait between starting each process, default 0.0
        results : Results
            The results object (see further below)
        processes : list[process.Process]
            A list of the processes currently running

    Methods:
        reset_simulation():
            Resets some values which may change during the simulation.

        _step_simulation(time=None):
            Steps the simulation by one time step. Handles things like
            adding and removing currently running nodes.

        list_nodes_and_ids():
            Prints out a list of each node in the graph and its ID
            Useful for the iterate_task_time() method.

        iterate_task_time():
            Runs several simulations while iterating the given task through the
            range specified. Returns a dictionary of Results object indexed by
            task time tested.

        simulate():
            Runs a simulation using the Simulation objects attributes.
    '''

    def __init__(self, file_name, n=1, t=0.0, timescale=1.0, time_step_length=1.0):
        '''
        Constructs the necessary attributes for the Simulation object

            Parameters:
                file_name : str
                    The name of the file within the project root folder
                n : int
                    How many processes to run in the simulation, default 1
                t : float
                    How much time to wait between starting each process, default 0.0               
                timescale : float
                    Speed multiplier of the simulation (for when the visualisation exists), default 1.0
                time_step_length : float
                    The length of each step in time, default 1.0
        '''

        if timescale <= 0:
            raise ValueError("timescale must be positive")
        if n < 1:
            raise ValueError("n must be >= 1")
        if t < 0.0:
            raise ValueError("t must be >= 0.0f")
        
        bpmn_xml = bpmn_parser.BpmnFile(file_name)
        process_graph = bpmn_xml.get_graph_structure()

        self.graph = process_graph 
        self.timescale = timescale
        self.time_step_length = time_step_length
        self.number_processes = n
        self.stagger = t
        self.results = Results(self.graph)
        self.processes = [process.Process(self.graph, i, start_time=i*self.time_step_length) for i in range(self.number_processes)]


    def reset_simulation(self):
        '''
        Resets the process objects for a fresh simulation.
        '''

        self.processes = [process.Process(self.graph, i, start_time=i*self.time_step_length) for i in range(self.number_processes)]

    def _step_simulation(self, time=None):
        '''
        Computes the changes made in one time step of the simulation.

            Parameters:
                time : float | None
                    The current time within the simulation
        '''

        finished_nodes = [[] for _ in self.processes]

        # Will be used to reserve slots for new nodes
        occupied = {}

        for process in self.processes:
            for running_node in process.current_running_nodes:
                occupied[running_node.id] = occupied.get(running_node.id, 0) + 1

        for process, finished in zip(self.processes, finished_nodes):
            nodes_added = []

            for node, time_left in process.current_running_nodes.items():
                # We don't need to worry about outgoing nodes if we are at the end.
                if node.id == self.graph.end.id:
                    if process.end_time is None:
                        process.end_time = time
                    pass
                elif time_left <= 0:
                    # does it fail at the end?
                    if random.random() < node.fail_chance:
                        process.current_running_nodes[node] = deepcopy(node.given_time)
                        self.results.fails[node.id] += 1
                        self.results.event_log.append(
                                {"time": time, "process": process.process_id, "node": node.name, "event": "failure"})

                    # it did not fail, so the children should be initialised
                    else:
                        # check if all of the current nodes "children" have leftover capacity
                        if all(
                                occupied.get(child.id, 0) < child.capacity
                                for child in node.outgoing
                                ):
                            finished.append(node)

                            if time is not None:
                                self.results.event_log.append(
                                        {"time": time, "process": process.process_id, "node": node.name, "event": "end", "waited": self.results.node_times_spent_waiting[node.id], "fails": self.results.fails[node.id]})

                            # reserve slot for each outgoing
                            if node.gateway_type == "AND":
                                for out in node.outgoing:
                                    occupied[out.id] = occupied.get(out.id, 0) + 1
                                    nodes_added.append(out)

                            # TODO ####################################################
                            # Currently, "XOR" gates will only move to one child,
                            # this is the correct behaviour. The chosen path to travel
                            # is decided ranomly with equal chance. This also isn't
                            # inherently bad. However, could be changed to better fit
                            # real life processes, where certain paths are chosen more
                            # than others.
                            # Regardless, an "XOR" node will only move to another node
                            # IF all of the child nodes have some capacity free.
                            # But this is not needed since not all children will be
                            # choses simultaniously, hence wasting some time in the sim.
                            elif node.gateway_type == "XOR" or node.gateway_type == "OR":
                                next_node = random.choice(node.outgoing)
                                occupied[next_node.id] = occupied.get(next_node.id, 0) + 1
                                nodes_added.append(next_node)

                        else:
                            self.graph.time_spent_waiting += self.time_step_length

                            for out in node.outgoing:
                                if occupied.get(out.id, 0) >= out.capacity:
                                    self.results.edge_times_spent_waiting[(node.id, out.id)] += self.time_step_length

                            self.results.node_times_spent_waiting[node.id] += self.time_step_length

                # there is still time left on the node 
                else:
                    process.current_running_nodes[node] -= self.time_step_length
            
            # Remove finished nodes
            for node in finished:
                del process.current_running_nodes[node]

            for node in nodes_added:
                process.current_running_nodes[node] = deepcopy(node.given_time)
                self.results.event_log.append(
                            {"time": time, "process": process.process_id, "node": node.name, "event": "start"})



    def list_nodes_and_ids(self):
        '''
        Prints out a list of each node in the graph and its ID
            Useful for the iterate_task_time() method.
        '''

        # Get the width of the left column (+1 for nicer look)
        max_len = max([len(node.name) for node in self.graph.nodes.values()]) + 1

        # print the table
        for nodeid in self.graph.nodes:
            node_name = self.graph.nodes[nodeid].name
            print(node_name + " "*(max_len - len(node_name)) + "| " + nodeid)

    def iterate_task_time(self, node_id, min_time, max_time, step):
        '''
        Runs as many simulations of the graph as specified by the ranges provided.
        For example, using min_time = 0, max_time = 100, step = 25, this function
        will run 5 simulations, each time replacing the sample time of the given node
        (node_id) with 0, 25, 50, 75, and 100 time steps.

            Parameters:
                node_id : str
                    The ID of the node to iterate over. Node IDs are defined when
                    making the BPMN file.
                min_time : float
                    The minimum sample time for the task
                max_time : float
                    The maximum sample time for the task (may not be reached)
                step : float
                    How much time to add for each simulation

            Returns:
                results_dict : dict[float, Results]
                    A dictionary of Results objects indexed by the time
                    taken for the task on that simulation.
        '''

        original_time = deepcopy(self.graph.nodes[node_id].sample_time)
        time_to_try = min_time
        results_dict = {}

        # iterate for each time_to_try
        # the range is simply how many time we can add `step` to the time_to_try
        # without exceeding max_time
        for i in range(int((max_time - min_time) // step + 1)):
            self.graph.nodes[node_id].sample_time = time_to_try
            results_dict[time_to_try] = self.simulate()
            time_to_try += step

        # reset
        self.graph.nodes[node_id].sample_time = original_time

        return results_dict

    def simulate(self, visualise=False):
        '''
        Runs a simulation using the Simulation objects attributes.

            Parameters:
                visualise : bool
                    If true, the simulation should be visualised on a graph.
                    This is currently not implemented.

            Returns:
                results : Results
                    The results object with data about the simulation
        '''

        if self.graph.start == None:
            raise Exception("No starting node was found")
        if self.graph.end == None:
            raise Exception("No end node was found")

        self.results = Results(self.graph)

        self.graph.reset_time_lefts() # randomise node.given_time

        # create fresh processes
        self.reset_simulation()

        if visualise:
            print("Visualisation not yet implemented :(")

        end_node_id = self.graph.end.id

        # start the simulation
        time_step = 0.0
        while True:
            # check if all nodes are at the end
            self._step_simulation(time=time_step)
            # Every process is either:
            #   - at the end node
            #   - or stuck somewhere with no outgoing edges
            if all(
                node.id == self.graph.end.id
                or (remaining_time <= 0 and len(node.outgoing) == 0)
                for process in self.processes
                for node, remaining_time in process.current_running_nodes.items()
            ):
                for process in self.processes:
                    if (
                        len(process.current_running_nodes) == 1
                        and self.graph.end in process.current_running_nodes
                    ):
                        process.possibly_stuck = False
                    else:
                        process.possibly_stuck = True

                break

            time_step += self.time_step_length

        self.results.time_steps_taken = time_step
        self.results.processes_ran = self.processes

        return self.results

class Results():
    '''
    A class to manage the results of a simulation

    Attributes:
        fails : dict[str, int]
            The number of times each node failed
        time_steps_taken : float
            !!!Should probably be renamed
            The length of the simulation, i.e. time until all nodes are done (or stuck)
        node_times_spent_waiting : dict[str, float]
            How long each node spent waiting to move on, despite being done
        edge_times_spent_waiting : dict[tuple[Node, Node], float]
            How long each edge was blocked from allowing a process to move along it
        event_log : list[dict[...]]
            An event log of any important point in the simulation
        graph : graph_structure.Graph
            The graph created in the Simulation object
        processes_ran : list[process.Process]
            A list of the processes which were ran. Each process has some
            useful data about it, such as the start and end times, and more.

    Methods:
        reset():
            Resets the results object for a fresh simulation, should that be required.

        processes_summary():
            Returns a dictionary of summaries of data for each of the n processes ran

        summary():
            Returns a short dictionary with vital information about the simulation

        find_bottlenecks():
            Returns a sorted list of nodes and and their 'bottleneck score'
    '''
    def __init__(self, graph):
        '''
        Constructs the necessary attributes for the Results object

            Parameters:
                graph : graph_structure.Graph
                    The graph created from the given BPMN file in Simulation()
        '''

        self.fails = {node_id: 0 for node_id in graph.nodes}
        self.time_steps_taken = 0.0
        self.node_times_spent_waiting = {node_id: 0.0 for node_id in graph.nodes}
        self.edge_times_spent_waiting = defaultdict(float)
        self.event_log = []
        self.graph = graph
        self.processes_ran = []

    def reset(self):
        '''
        Resets the results object for a fresh simulation, should that be required.
        '''

        self.__init__(self.graph)

    def processes_summary(self):
        '''
        Returns a dictionary of process several data values about each
        simulation, indexed by the ID of each process.

            Parameters:
                None

            Returns:
                dict[int, dict[str, float]]
                    The dictionary of dictionaries containing data about each process
        '''

        output = {}
        for process in self.processes_ran:
            output[process.process_id] = {"Start time": process.start_time, "End time": process.end_time}

        return output

    def find_bottlenecks(self):
        '''
        Returns a list of nodes listed by their bottleneck score.

        We will score the bottleneck of a node by
        two parameters: how much time it wastes, and how many times it failed.
        We compute: fails * sum_{sources in node.incoming} (source.time_spent_waiting)

            Parameters:
                None
            
            Returns:
                list[dict[str, str | str, float]
                    The list of node ids and bottlenecks score, sorted by score (reversed).
        '''

        bottlenecks = []
        for node in self.graph.nodes.values():
            fails = self.fails[node.id]

            time_wasted = sum(
                self.edge_times_spent_waiting.get((source.id, node.id), 0)
                for source in node.incoming
            )

            bottlenecks.append({"node_id": node.id, "node": node.name, "score": ((fails+1) * time_wasted + fails) / 100.0})

        return sorted(bottlenecks, key=lambda x: x["score"], reverse=True)

    def summary(self):
        '''
        Returns a short summary of the results
        '''

        return {
            "simulation_time": self.time_steps_taken,
            "total_failures": sum(self.fails.values()),
            "total_waiting_time": sum(self.edge_times_spent_waiting.values()),
            "top 3 bottlenecks": [bn["node"] for bn in self.find_bottlenecks()[:3]]
        }
