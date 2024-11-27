model scenic.simulators.beamng.model

behavior Autopilot90Behavior():
    do AutopilotBehavior()
    print("setting speed to 90")
    take AISetSpeedAction(speed=90, mode='set')

spot = new OrientedPoint at (-717, 111, 118)
ego = new Vehicle at spot,
    with vid 'new',
    with model 'etk800',
    with behavior Autopilot90Behavior()