beamngpy = None
try:
    import beamngpy
except ImportError:
    pass
if beamngpy:
    from .simulator import BeamNGSimulator
del beamngpy