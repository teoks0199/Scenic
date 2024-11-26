model scenic.simulators.beamng.model

behavior TurnLeft():
    delay = 30
    last_stop = simulation().currentTime

    while True:
        try:
            do AutopilotBehavior()
        interrupt when simulation().currentTime - last_stop > delay:
            print("Turning left")
            do TurnLeftBehavior()
            break

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior TurnLeft()