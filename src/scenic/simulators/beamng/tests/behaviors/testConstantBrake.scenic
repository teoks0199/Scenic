model scenic.simulators.beamng.model

behavior BrakeBehavior():
    delay = 10
    last_stop = simulation().currentTime

    while True:
        try:
            do ConstantThrottleBehavior(0.5)
        interrupt when simulation().currentTime - last_stop > delay:
            print("Braking")
            do ConstantBrakeBehavior(1.0)
            break

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior BrakeBehavior()