# does not behave as expected

param beamng_map = "gridmap_v2"

model scenic.simulators.beamng.model

ego = new Vehicle at (717, 111, 108),
    with vid 'new',
    with model 'etk800',

second = new Vehicle left of ego by 10,
    with vid 'second',
    with model 'etk800',
    with color (0.2, 0.7, 0.9, 0)