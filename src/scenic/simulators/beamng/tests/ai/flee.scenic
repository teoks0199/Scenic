model scenic.simulators.beamng.model

behavior FleeBehavior():
    take AISetTargetAction(target_vid='chaser')
    take AISetFleeAction()

behavior ChaseBehavior():
    take AISetTargetAction(target_vid='ego')
    take AISetChaseAction()

chaser = new Vehicle at (-715, 121, 118),
    with vid 'chaser',
    with model 'etk800',
    with behavior ChaseBehavior()

ego = new Vehicle at (-717, 111, 118),
    with vid 'ego',
    with model 'etk800',
    with behavior FleeBehavior()