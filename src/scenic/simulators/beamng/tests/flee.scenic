model scenic.simulators.beamng.model

behavior FleeBehavior():
    take AISetTargetAction(target_vid='target')
    take AISetFleeAction()

behavior ChaseBehavior():
    take AISetTargetAction(target_vid='ego')
    take AISetChaseAction()

target = new Vehicle at (-715, 121, 118),
    with vid 'target',
    with model 'etk800',
    with pos (-715, 121, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior ChaseBehavior()

ego = new Vehicle at (-717, 111, 118),
    with vid 'ego',
    with model 'etk800',
    with pos (-717, 111, 118),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior FleeBehavior()