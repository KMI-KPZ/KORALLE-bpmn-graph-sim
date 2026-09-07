import time
import pandas as pd

import graph_simulation as gsim
my_sim = gsim.Simulation("complexdiagram.bpmn", n=1, t=0.2, time_step_length=0.1)

my_sim.list_nodes_and_ids()

results_dict = my_sim.iterate_task_time("Activity_0m0xrzd", 0.0, 100.0, 25.0)

for test in results_dict:
    print(f"Time for task: {test}".center(30, "*"))
    summary = results_dict[test].summary()
    for line in summary:
        print(line + ":", summary[line])

    print("\n" * 2)

print(my_sim.simulate().summary())

