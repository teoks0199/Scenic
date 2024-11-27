model scenic.simulators.beamng.model

behavior SetPositionBehavior(pos=(-600, 50, 118)):
    take SetPositionAction(pos)

ego = new Vehicle at (-717, 111, 118),
    with vid 'new',
    with model 'etk800',
    with behavior SetPositionBehavior((-600, 50, 118))
