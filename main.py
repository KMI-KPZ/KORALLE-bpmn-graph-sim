import time
import pandas as pd

import testing
import graph_simulation as gsim

testing.test1()
testing.test2()
testing.test3()
testing.test4()
testing.test5()
testing.test6()

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
