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

class SetThrottleAction(Action):
    """Set the throttle.

    Arguments:
        throttle: Throttle value between 0 and 1.
    """

    def __init__(self, throttle: float):
        if not 0.0 <= throttle <= 1.0:
            raise RuntimeError("Throttle must be a float in range [0.0, 1.0].")
        self.throttle = throttle

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.control(throttle=self.throttle)

class SetSteerAction(Action):
    """Set the steering 'angle'.

    Arguments:
        steer: Steering 'angle' between -1 and 1.
    """

    def __init__(self, steer: float):
        if not -1.0 <= steer <= 1.0:
            raise RuntimeError("Steer must be a float in range [-1.0, 1.0].")
        self.steer = steer

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.control(steering=self.steer)

class SetBrakeAction(Action):
    """Set the amount of brake.

    Arguments:
        brake: Amount of braking between 0 and 1.
    """

    def __init__(self, brake: float):
        if not 0.0 <= brake <= 1.0:
            raise RuntimeError("Brake must be a float in range [0.0, 1.0].")
        self.brake = brake

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.control(brake=self.brake)

class SetHandBrakeAction(Action):
    """Set or release the hand brake.

    Arguments:
        handBrake: Whether or not the hand brake is set.
    """

    def __init__(self, handBrake: bool):
        if not isinstance(handBrake, bool):
            raise RuntimeError("Hand brake must be a boolean.")
        self.handbrake = handBrake

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        if self.handbrake:
            vehicle.control(parkingbrake=1)
        else:
            vehicle.control(parkingbrake=0)

class SetReverseAction(Action):
    """Engage or release reverse gear.

    Arguments:
        reverse: Whether or not the car is in reverse.
    """

    def __init__(self, reverse: bool):
        if not isinstance(reverse, bool):
            raise RuntimeError("Reverse must be a boolean.")
        self.reverse = reverse

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        if self.reverse:
            vehicle.control(gear=-1)
        else:
            vehicle.control(gear=2)

class SetGearAction(Action):
    """Set the gear of a vehicle to shift to."""
    def __init__(self, gear):
        if not isinstance(gear, int):
            raise RuntimeError("Gear must be an int.")
        self.gear = gear # -1 eq backwards, 0 eq neutral, 1 to X eq nth gear

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.control(gear=self.gear)

class SetVelocityAction(Action):
    """Set the velocity of a vehicle."""

    def __init__(self, vel: float, dt: float = 1.0):
        self.velocity = vel
        self.dt = dt # default dt is suitable up to 30 m/s

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.set_velocity(self.velocity, self.dt)

class SetPositionAction(Action):
    """Teleport an vehicle to the given position."""

    def __init__(self, pos: Vector, yaw: float = None, pitch: float = None, roll: float = None):
        self.pos = pos
        self.yaw = yaw
        self.pitch = pitch
        self.roll = roll

    def applyTo(self, obj, sim):
        vechicle = sim.scenario.get_vehicle(obj.vid)
        # pos = utils.scenicToBeamNGVector(self.pos)
        pos = self.pos
        if self.yaw and self.pitch and self.roll:
            rot_quat = utils.euler_to_quaternion(self.yaw, self.pitch, self.roll)
            vechicle.teleport(pos, rot_quat)
        else:
            vechicle.teleport(pos)

class SetManualGearShiftAction(Action):
    def __init__(self, manualGearShift):
        if not isinstance(manualGearShift, bool):
            raise RuntimeError("Manual gear shift must be a boolean.")
        self.manualGearShift = manualGearShift

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        if self.manualGearShift:
            vehicle.set_shift_mode('realistic_manual')

class SetShiftModeAction(Action):
    def __init__(self, mode):
        if mode not in ['realistic_manual', 'realistic_manual_auto_clutch', 'arcade', 'realistic_automatic']:
            raise RuntimeError("Shifting mode must be 'realistic_manual', 'realistic_manual_auto_clutch', 'arcade', or 'realistic_automatic'.")
        self.mode = mode

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.set_shift_mode(self.mode)

class SetClutchAction(Action):
    """Set the level of the clutch of a vehicle."""
    def __init__(self, clutch):
        if not isinstance(clutch, float):
            raise RuntimeError("Clutch must be a float.")
        self.clutch = clutch # from 0.0 to 1.0

    def applyTo(self, obj, sim):
        vehicle = sim.scenario.get_vehicle(obj.vid)
        vehicle.control(clutch=self.clutch)

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