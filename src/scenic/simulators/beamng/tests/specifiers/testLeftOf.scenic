param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

ego = new Vehicle at (-717, 111, 108),
    with vid 'new',
    with model 'etk800'

second = new Vehicle left of ego by 10,
    with vid 'second',
    with model 'etk800',
    facing directly toward ego
