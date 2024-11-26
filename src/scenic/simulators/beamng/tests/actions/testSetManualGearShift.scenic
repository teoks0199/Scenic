model scenic.simulators.beamng.model

behavior SetManualBehavior():
    delay = 10
    last_stop = simulation().currentTime

    while True:
        try:
            do ConstantThrottleBehavior()
        interrupt when simulation().currentTime - last_stop > delay:
            print("Setting manual gear shift")
            take SetManualGearShiftAction(True)
            break

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior SetManualBehavior()
