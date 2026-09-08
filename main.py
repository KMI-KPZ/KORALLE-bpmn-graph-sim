import pandas as pd

import graph_simulation as gsim

my_sim = gsim.Simulation("complexdiagram.bpmn", n=5, t=1, time_step_length=0.5)
results = my_sim.simulate()
print(pd.DataFrame(results.event_log).to_string())

"""
# An example of the iterate_task_time function

mysim = gsim.Simulation("complexdiagram.bpmn", n=100, t=1, time_step_length=1)
results_dict = mysim.iterate_task_time("Activity_0bsr565", 0, 100, 25)

for result in results_dict:
    print(result)
    summary = results_dict[result].summary()

    for line in summary:
        print(line + ":", summary[line])

    print("\n"*3)
"""
