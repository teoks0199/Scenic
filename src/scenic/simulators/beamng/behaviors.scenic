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