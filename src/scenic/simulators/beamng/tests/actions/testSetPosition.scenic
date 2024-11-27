model scenic.simulators.beamng.model

behavior SetPositionBehavior(pos=(-600, 50, 108)):
    take SetPositionAction(pos)

ego = new Vehicle at (-717, 111, 118),
    with vid 'new',
    with model 'moonhawk',
    with behavior SetPositionBehavior((-600, 50, 108))
