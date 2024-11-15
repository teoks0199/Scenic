import math

import beamngpy

from scenic.core.vectors import Orientation, Vector


def beamNGToScenicVector(vec):
    return Vector(vec[0], vec[1], vec[2])

def scenicToBeamNGVector(vec):
    return (vec.x, vec.y, vec.z)

def quaternion_to_euler(quaternion):
    qx, qy, qz, qw = quaternion

    # Yaw (rotation around Z-axis)
    yaw = math.atan2(2.0 * (qw * qz + qx * qy), 1.0 - 2.0 * (qy * qy + qz * qz))
    
    # Pitch (rotation around Y-axis)
    sinp = 2.0 * (qw * qy - qz * qx)
    pitch = math.copysign(math.pi / 2, sinp) if abs(sinp) >= 1 else math.asin(sinp)
    
    # Roll (rotation around X-axis)
    roll = math.atan2(2.0 * (qw * qx + qy * qz), 1.0 - 2.0 * (qx * qx + qy * qy))
    
    return yaw, pitch, roll

def euler_to_quaternion(yaw, pitch, roll):
    # Compute the half angles
    cy = math.cos(yaw * 0.5)
    sy = math.sin(yaw * 0.5)
    cp = math.cos(pitch * 0.5)
    sp = math.sin(pitch * 0.5)
    cr = math.cos(roll * 0.5)
    sr = math.sin(roll * 0.5)

    # Compute the quaternion components
    qw = cr * cp * cy + sr * sp * sy
    qx = sr * cp * cy - cr * sp * sy
    qy = cr * sp * cy + sr * cp * sy
    qz = cr * cp * sy - sr * sp * cy

    return qx, qy, qz, qw