model scenic.simulators.beamng.model
behavior DriveToWaypointBehavior():
    delay = 20
    last_stop = simulation().currentTime
    while True:
        try:
            do AutopilotBehavior()
        interrupt when simulation().currentTime - last_stop > delay:
            print("moving to waypoint")
            take AISetWaypointAction()
            take AISetManualAction()
            break

ego = new Vehicle at (-717, 111, 118),
    with vid 'ego',
    with model 'etk800',
    with behavior DriveToWaypointBehavior()