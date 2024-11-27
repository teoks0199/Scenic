param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

behavior SetHandBrakeBehavior():
    delay = 12
    last_stop = simulation().currentTime
    try:
        do ConstantThrottleBehavior(0.5)
    interrupt when simulation().currentTime - last_stop > delay:
        print("Releasing throttle")
        take SetThrottleAction(0.0)
        print("Activating Handbrake")
        take SetHandBrakeAction(True)

ego = new Vehicle at (-717, 111, 108),
    with vid 'new',
    with model 'etk800',
    with behavior SetHandBrakeBehavior()
