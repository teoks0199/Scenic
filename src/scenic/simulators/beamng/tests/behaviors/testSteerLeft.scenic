param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

behavior DriveAndSteerLeftBehavior():
    delay = 10
    last_stop = simulation().currentTime
    try:
        do ConstantThrottleBehavior(0.5)
    interrupt when simulation().currentTime - last_stop > delay:
        print("Turning left")
        do SteerLeftBehavior()

ego = new Vehicle at (-717, 111, 108),
    with vid 'new',
    with model 'etk800',
    with behavior DriveAndSteerLeftBehavior()