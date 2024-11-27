model scenic.simulators.beamng.model
behavior StopBehavior():
    delay = 20
    last_stop = simulation().currentTime
    while True:
        try:
            do AutopilotBehavior()
        interrupt when simulation().currentTime - last_stop > delay:
            print("Stopping")
            take AISetStoppingAction()
            break

ego = new Vehicle at (-717, 111, 118),
    with vid 'ego',
    with model 'etk800',
    with behavior StopBehavior()