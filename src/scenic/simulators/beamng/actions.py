try:
    from beamngpy import BeamNGpy, Scenario, Vehicle
    from beamngpy.sensors import (
    AdvancedIMU,
    Camera,
    Damage,
    Electrics,
    Lidar,
    State,
    Timer,
    Ultrasonic,
)
except ImportError as e:
    raise ModuleNotFoundError('beamNG scenarios require the "beamngpy" Python package') from e

import scenic.simulators.beamng.utils.utils as utils
from scenic.core.simulators import * # imports the Action superclass

class SetAutopilotAction(Action):
    def __init__(self, enabled):
        if not isinstance(enabled, bool):
            raise RuntimeError("Enabled must be a boolean.")
        self.enabled = enabled

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('span')