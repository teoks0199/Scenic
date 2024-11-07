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

# class BeamNGObject:
#     """
#     Instance variables are assigned with the colon
#     like in Python dataclasses, whereas class variables
#     are assigned with '='
#     """
#     id: None
#     name: None
#     type: None
#     pos: None
#     rot: None
#     scale: None
#     opts: None
#     children: None
class Car:
    vid: None
    model: 'etk800'