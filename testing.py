import pandas as pd
import graph_simulation as gsim


def test1():
    # Look at test 1 event logs
    test1_simulation = gsim.Simulation("tests/test1.bpmn", n=1)
    test1_results = test1_simulation.simulate()
    test1_event_log = pd.DataFrame(test1_results.event_log)

    print("Test 1 event log with n=1")
    print(test1_event_log.to_string())
    print("\n"*2)

def test2():
    # Look at test 2 event logs
    test2_simulation = gsim.Simulation("tests/test2.bpmn", n=1, t=1)
    test2_results = test2_simulation.simulate()
    test2_event_log = pd.DataFrame(test2_results.event_log)

    print("Test 2 event log with n=1")
    print(test2_event_log.to_string())
    print("\n"*2)

def test3():
    # Look at test 3 event logs
    # this one needs both n=1 and n>1
    test3_n_1 = gsim.Simulation("tests/test3.bpmn", n=1)
    test3_n_3 = gsim.Simulation("tests/test3.bpmn", n=3)

    test3_n_1_results = test3_n_1.simulate()
    test3_n_3_results = test3_n_3.simulate()

    test3_n_1_log = pd.DataFrame(test3_n_1_results.event_log)
    test3_n_3_log = pd.DataFrame(test3_n_3_results.event_log)

    print("Test 3 event log with n=1")
    print(test3_n_1_log.to_string())
    print("\n"*2)


    print("Test 3 event log with n=3")
    print(test3_n_3_log.to_string())
    print("\n"*2)

def test4():
    # Look at test 4 event logs
    # this one needs both n=1 and n>1
    test4_n_1 = gsim.Simulation("tests/test4.bpmn", n=1)
    test4_n_3 = gsim.Simulation("tests/test4.bpmn", n=3)

    test4_n_1_results = test4_n_1.simulate()
    test4_n_3_results = test4_n_3.simulate()

    test4_n_1_log = pd.DataFrame(test4_n_1_results.event_log)
    test4_n_3_log = pd.DataFrame(test4_n_3_results.event_log)

    print("Test 4 event log with n=1")
    print(test4_n_1_log.to_string())
    print("\n"*2)

    print("Test 4 event log with n=3")
    print(test4_n_3_log.to_string())
    print("\n"*2)

def test5():
    # Look at test 5 event logs
    # this one needs both n=1 and n>1
    test5_n_1 = gsim.Simulation("tests/test5.bpmn", n=1)
    test5_n_3 = gsim.Simulation("tests/test5.bpmn", n=3)

    test5_n_1_results = test5_n_1.simulate()
    test5_n_3_results = test5_n_3.simulate()

    test5_n_1_log = pd.DataFrame(test5_n_1_results.event_log)
    test5_n_3_log = pd.DataFrame(test5_n_3_results.event_log)

    print("Test 5 event log with n=1")
    print(test5_n_1_log.to_string())
    print("\n"*2)

    print("Test 5 event log with n=3")
    print(test5_n_3_log.to_string())
    print("\n"*2)


def test6():
    # Take test 6 summary
    # needs n=100
    test6 = gsim.Simulation("tests/test6.bpmn", n=100)
    test6_results = test6.simulate()
    test6_summary = test6_results.summary()

    print("Test 6 summary with n=100")
    print(test6_summary)

