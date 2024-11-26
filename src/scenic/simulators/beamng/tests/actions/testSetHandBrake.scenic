model scenic.simulators.beamng.model

behavior SetHandBrakeBehavior():
    delay = 10
    last_stop = simulation().currentTime

    while True:
        try:
            do ConstantThrottleBehavior()
        interrupt when simulation().currentTime - last_stop > delay:
            print("Activating Handbrake")
            take SetHandBrakeAction(1.0)
            break

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior SetHandBrakeBehavior()
