model scenic.simulators.beamng.model

behavior SetPositionBehavior(pos=(-600, 50, 118)):
    take SetPositionAction(pos)

spot = new OrientedPoint at (-717, 111, 118)
ego = new Vehicle, #at spot,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior SetPositionBehavior((-600, 50, 118))