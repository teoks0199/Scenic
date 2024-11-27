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
    while True:
        take SetThrottleAction(x), SetReverseAction(False), SetHandBrakeAction(False)

behavior ConstantBrakeBehavior(x):
    while True:
        take SetThrottleAction(0), SetBrakeAction(x), SetReverseAction(False), SetHandBrakeAction(False)

behavior SteerLeftBehavior():
    take SetSteerAction(-0.5)

behavior SteerRightBehavior():
    take SetSteerAction(0.5)

behavior ReverseBehavior():
    take SetReverseAction(True), SetHandBrakeAction(False), SetThrottleAction(0.5)