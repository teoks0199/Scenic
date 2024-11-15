"""Scenic world model for traffic scenarios in beamNG.
"""
#from scenic.domains.driving.model import *
try:
    from scenic.simulators.beamng.simulator import BeamNGSimulator
    from scenic.simulators.beamng.behaviors import *
    from scenic.simulators.carla.actions import *
except ImportError as e:
    raise ImportError("To use the BeamNG simulator, please install the 'scenic' package with the 'beamng' extra") from e

try:
    simulator BeamNGSimulator()
except Error as e:
    raise Error("Failed to initialize BeamNG simulator") from e

class BeamNGObject: # ScenarioObject in BeamNG
    oid: None
    name: None
    otype: None
    scale: None
    options: None
    pos: None
    rot_quat: None
    
class Vehicle(BeamNGObject):
    vid: None
    model: None    