param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

behavior SetVelocityBehavior(vel=30):
    take SetVelocityAction(vel)

ego = new Vehicle at (-717, 111, 108),
    with vid 'new',
    with model 'etk800',
    with behavior SetVelocityBehavior(30)
