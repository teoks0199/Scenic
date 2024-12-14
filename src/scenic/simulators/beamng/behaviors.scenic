try:
    from scenic.simulators.beamng.actions import *
except ModuleNotFoundError:
    pass    # ignore; error will be caught later if user attempts to run a simulation

behavior AutopilotBehavior():
    """Behavior causing a vehicle to use BeamNG's built-in autopilot."""
    take AISetAutopilotAction()

behavior RandomBehavior():
    """Drive from random points to random points on the map."""
    take AISetRandomAction()

behavior ConstantThrottleBehavior(x):
    """Drive forward at a constant throttle setting."""
    while True:
        take SetThrottleAction(x), SetReverseAction(False), SetHandBrakeAction(False)

behavior ConstantBrakeBehavior(x):
    """Brake at a constant setting."""
    while True:
        take SetThrottleAction(0), SetBrakeAction(x), SetReverseAction(False), SetHandBrakeAction(False)

behavior SteerLeftBehavior():
    """Steer left."""
    take SetSteerAction(-0.5)

behavior SteerRightBehavior():
    """Steer right."""
    take SetSteerAction(0.5)

behavior ReverseBehavior():
    """Drive in reverse."""
    take SetReverseAction(True), SetHandBrakeAction(False), SetThrottleAction(0.5)