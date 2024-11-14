"""Scenic world model for traffic scenarios in beamNG.
"""

try:
    from scenic.simulators.beamng.simulator import BeamNGSimulator
except ImportError as e:
    raise ImportError("To use the BeamNG simulator, please install the 'scenic' package with the 'beamng' extra") from e

try:
    simulator BeamNGSimulator()
except Error as e:
    raise Error("Failed to initialize BeamNG simulator") from e

class BeamNGObject:
    pos: None
    rot_quat: None
    
class Vehicle(BeamNGObject):
    vid: None
    model: None

class ScenarioObject(BeamNGObject):
    oid: None
    name: None
    otype: None
    scale: None
    options: None