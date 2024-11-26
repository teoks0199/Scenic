param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

behavior SetVelocityBehavior(vel=30):
    take SetVelocityAction(vel)

ego = new Vehicle,
    with vid 'new',
    with model 'etk800',
    with pos (-717, 111, 108),
    with rot_quat (0, 0, 0.3826834, 0.9238795),
    with behavior SetVelocityBehavior(30)
