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

class AISetAutopilotAction(Action):
    """Drive along the entire road network of the map
    """
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('span')

class AISetStoppingAction(Action):
    """Make the vehicle come to a halt (AI disables itself once the vehicle stopped.)
    """
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('stopping')

class AISetManualAction(Action):
    """Drive to a specific waypoint, target set separately.
    """
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('manual')

class AISetRandomAction(Action):
    """Drive from random points to random points on the map
    """
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('random')

class AISetChaseAction(Action):
    """Chase a target vehicle, target set separately
    """
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('chase')

class AISetFleeAction(Action):
    """Flee from a vehicle, target set separately
    """
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_mode('flee')

class AISetSpeedAction(Action):
    """Sets the target speed for the AI in m/s. Speed can be maintained in two modes:

    limit: Drive speeds between 0 and the limit, as the AI
    sees fit.

    set: Try to maintain the given speed at all times.
    """
    def __init__(self, speed, mode='limit'):
        self.speed = speed
        self.mode = mode

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_speed(self.speed, self.mode)

class AISetTargetAction(Action):
    """Sets the target to chase or flee. 
    The target should be the ID of another vehicle in the simulation. 
    The AI is automatically set to the given mode.
    """
    def __init__(self, target=None, target_vid=None, mode='chase'):
        if target:
            self.target_vid = target.vid
        if target_vid:
            self.target_vid = target_vid
        if self.target_vid is None:
            raise ValueError('Target vehicle ID must be provided')
        self.mode = mode

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.ai.set_target(self.target_vid, self.mode)

class AISetWaypointAction(Action):
    """Sets the waypoint the AI should drive to in manual mode. 
    The AI gets automatically set to manual mode when this method is called."""
    def __init__(self):
        pass

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        waypoint = sim.scenario.find_waypoints()[5] # example waypoint
        print(waypoint.name)
        vehicle.ai.set_waypoint(waypoint.name)