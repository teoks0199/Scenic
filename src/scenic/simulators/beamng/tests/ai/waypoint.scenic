model scenic.simulators.beamng.model
behavior DriveToWaypointBehavior():
    delay = 30
    last_stop = simulation().currentTime

    while True:
        try:
            do AutopilotBehavior()
        interrupt when simulation().currentTime - last_stop > delay:
            print("moving to waypoint")
            take AISetWaypointAction()
            take AISetManualAction()
            break

ego = new Vehicle,
    with vid 'ego',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior DriveToWaypointBehavior()