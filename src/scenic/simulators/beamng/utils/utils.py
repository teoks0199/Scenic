import math

import beamngpy

from scenic.core.vectors import Orientation, Vector


def beamNGToScenicVector(vec):
    return Vector(vec[0], vec[1], vec[2])
