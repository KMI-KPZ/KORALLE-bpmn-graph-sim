# BPMN Simulation using Directed Graphs

A simple Python-based simulator for processes modeled as **BPMN graphs**.

The project reads a BPMN 2.0 file, converts the process into a graph structure, and simulates the flow of work through the process.

## Table of Contents

- [BPMN Simulation using Directed Graphs](#bpmn-simulation-using-directed-graphs)
- [Repository Structure](#repository-structure)
- [Usage](#usage)
- [BPMN Requirements](#bpmn-requirements)
  - [Task Naming](#task-naming)
  - [Layout](#layout)
- [Detailed Usage](#detailed-usage)
  - [The Results Object](#the-results-object)
    - [Total Simulation Time](#total-simulation-time)
    - [Time Wasted](#time-wasted)
    - [Failures](#failures)
    - [Event Log](#event-log)
    - [Processes](#processes)
    - [Bottlenecks](#bottlenecks)
- [Simulation Options](#simulation-options)
- [Iterating Values for a Simulation](#iterating-values-for-a-simulation)
- [Contributing](#contributing)
- [License](#license)

## Repository Structure
```text
.
├── bpmn_parser.py          # Turns a BPMN file into a Graph object
├── complexdiagram.bpmn     # Example BPMN file for testing
├── graph_simulation.py     # The file in charge of handling simulations
├── graph_structure.py      # Defines the Graph and Node classes
├── main.py                 # Example usage of graph_simulation
├── process.py              # Defines the Process class
├── README.md               # Do as the name say ;)
├── testing.py              # Running tests in tests/
└── tests/                  # Folder containing test BPMN files
    ├── test1.bpmn
    └── ...
```

## Usage

Clone the repository with

```bash
git clone https://github.com/toewl-devv/KORALLE-bpmn-graph-sim.git
```

Run the example main program:

```bash
python3 main.py
```
or read on to find out more about how to use this simulator (an example diagram
is provided in `complexdiagram.bpmn`.

## BPMN Requirements
### Task Naming

When creating a BPMN process diagram, a name can be given to each process.
The name must have a very specific format:
```
name; time; variance; capacity; fail_chance; gateway_type
```
Where:

| Parameter      | Description                                          |
| -------------- | ---------------------------------------------------- |
| `name`         | Name of the task                                     |
| `time`         | Average processing time                              |
| `variance`     | Processing-time variance                             |
| `capacity`     | Number of tasks that can be processed simultaneously |
| `fail_chance`  | Probability of task failure, between `0` and `1`     |
| `gateway_type` | `AND`, `OR`, or `XOR`                                |

If these parameters are not specified, somesome  default values are used.

### Layout
The BPMN diagram must have "start event" and "end event" nodes. This is so that the simulation knows
where to begin and end the simulation.

A name musn't be given to these nodes, as they will automatically be made to take 0 time units
and have (practically) infinite capacity.

## Detailed Usage

To begin, the `main` file must import the simulation library:
```python
import graph_simulation as gsim
```

From there, we can create our first, basic simulation using
the `Simulation` class:

```python
my_sim = gsim.Simulation("complexdiagram.bpmn")
```

To run the simulation and store the given `Results` object, we use

```python
results = my_sim.simulate()
```

### The Results Object

Every time a simulation is run, a `Results` object is created 
with several attributes which can be used to analyze the simulation.

A summary of the results is given by:
```python
print(results.summary())
```

An extensive list of all of the capabilities of the `Result` class is below.

#### Total Simulation Time
The total time taken to finish the simulation is given by
```python
results.time_steps_taken
```
#### Time Wasted
The total time wasted can be found in different ways. First is 
node-wise wasted time, which is incremented whenever a process *could*
move from one node to the next but is blocked since the next node(s) is
at full capacity.
```python
print(results.node_times_spent_waiting)
```

The second is edge-wise wasted time, which is incremented when a process specifically cannot move
along that edge because that edge is blocked due to capacity.
```python
print(results.edge_times_spent_waiting)
```

#### Failures
Sometimes, nodes can fail. We can see which nodes failed how many times using
```python
print(results.fails)
```

#### Event Log
The event log is a list of every event which happened in the simulation.
Each entry in the log has a timestamp, a process ID, and the specific event which occured.

> [!NOTE] The `pandas` library is very useful for viewing the event log (as well all previous attributes).
```python
import pandas as pd
print(pd.DataFrame(results.event_log).to_string())
```

#### Processes
We can access a list of the `Process` objects which were ran in the simulation using
```python
print(results.processes_ran)
```
However, this isn't very useful. Each process object has a few attributes which may be useful:
```
start_time
end_time
possibly_stuck
```
Otherwise, we may run
```python
print(results.processes_summary())
```

to see a summary of what each process did. This returns a dictionary of dictionaries.

#### Bottlenecks
We can use
```python
results.find_bottlenecks()
```
to return a list sorted from highest to lowest in order of each nodes "bottleneck score".

### Simulation Options
When creating a `Simulation` object, there are several customisable parameters:
```python
my_sim = gsim.Simulation("complexdiagram.bpmn", n=1, t=0.0, timescale=1.0, time_step_length=1.0)
```
Where
| Parameter          | Meaning                                                          | Default |
|--------------------|------------------------------------------------------------------|---------|
| `n`                | Number of processes to run in the simulation                     | 1       |
| `t`                | Stagger time between beginning each process                      | 0.0     |
| `timescale`        | The speed multiplier of the simulation (should it be visualised) | 1.0     |
| `time_step_length` | The "minimum time unit" for the simulation                       | 1.0     |

When running the simulation using `my_sim.simulate()`, one can optionally use
```python
my_sim.simulate(visualise=True)
```
which will run a visualisation of the simulation.
> [!NOTE] This isn't actually implemented yet.

### Iterating Values for a Simulation
Suppose we want to test out if making a particular node faster will help the overall process become faster.
First we require the node ID. This can be found by running
```python
my_sim.list_nodes_and_ids()
```
which will print a table of each node name and its respective ID.

When we have found the ID we would like to iterate, we can use
```python
results_dictionary = my_sim.iterate_task_time(node_id, 0.0, 10.0, 2.5)
```
to run a simulation where that node takes 0, 2.5, 5, 7.5, and 10 time units.

The results from each simulation is kept in a dictionary of `Results` objects, which is indexed by the task time, e.g.
```text
{
    0.0: Results
    2.5: Results
    ...
}
```

# Contributing
* Use python >= 3
* Follow current styling and python standards. I.e. snake_case, docstring formatting, etc.

# License
?

