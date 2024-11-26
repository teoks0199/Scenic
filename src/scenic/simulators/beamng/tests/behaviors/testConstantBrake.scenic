param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

behavior ThrottleAndBrakeBehavior():
    delay = 15
    last_stop = simulation().currentTime
    try:
        print("Accelerating")
        do ConstantThrottleBehavior(0.5)
    interrupt when simulation().currentTime - last_stop > delay:
        print("Braking")
        do ConstantBrakeBehavior(1.0)

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 108),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior ThrottleAndBrakeBehavior()
