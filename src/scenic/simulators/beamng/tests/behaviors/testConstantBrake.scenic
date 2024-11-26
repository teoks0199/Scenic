model scenic.simulators.beamng.model

param beamng_map = "gridmap_v2"

behavior BrakeBehavior():
    delay = 10
    last_stop = simulation().currentTime

    while True:
        try:
            print("Setting shift mode to realistic_manual_auto_clutch")
            take SetShiftModeAction("realistic_manual_auto_clutch")
            print("Setting gear to 1")
            take SetGearAction(1)
            print("Accelerating")
            do ConstantThrottleBehavior(0.5)
        interrupt when simulation().currentTime - last_stop > delay:
            print("Braking")
            do ConstantBrakeBehavior(1.0)
            break

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 108),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior BrakeBehavior()
