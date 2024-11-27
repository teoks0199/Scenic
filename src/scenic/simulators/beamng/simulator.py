"""Simulator interface for beamNG."""

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
import logging
import math
import os
import traceback
import warnings

import scenic.core.errors as errors
from scenic.core.simulators import Simulation, SimulationCreationError, Simulator
from scenic.domains.driving.simulators import DrivingSimulation, DrivingSimulator
import scenic.simulators.beamng.utils.utils as utils
from scenic.core.vectors import Vector
from scenic.core.simulators import SimulationCreationError
from scenic.syntax.veneer import verbosePrint
class BeamNGSimulator(DrivingSimulator):
    def __init__(
            self,
            scenario_level,
            scenario_name='example', 
            scenario_path=None,
            host='localhost', 
            port=64256, 
            bng_path='D:\\BeamNG\\BeamNG.tech.v0.33.3.0', 
            timestep=0.1
    ):
        super().__init__()
        print("Initializing BeamNG simulator")

        verbosePrint(f"Connecting to BeamNGpy on port {port}")
        self.bng = BeamNGpy(host=host, port=port, home=bng_path)
        self.bng.open()
        if scenario_path is not None:
            try:
                self.scenario = Scenario(level=scenario_level, name=scenario_name, path=scenario_path)
            except Exception as e:
                raise RuntimeError(f"BeamNG could not load scenario {scenario_name} from '{scenario_path}'") from e
        else:
            scenario = Scenario(level=scenario_level, name=scenario_name) # arbitrary scenario
            ego = Vehicle("initial", model="etk800", color="White", license="initial_car")
            scenario.add_vehicle(
                ego, pos=(-717, 101, 0), rot_quat=(0.0010, 0.1242, 0.9884, -0.0872)
            )
            scenario.make(self.bng)
            self.scenario = scenario
        self.timestep = timestep
        self.bng.settings.set_steps_per_second(1 / self.timestep)
        self.bng.scenario.load(self.scenario)
        self.bng.scenario.start()
        self.scenario_number = 0  # Number of the scenario executed
        
    def createSimulation(self, scene, timestep, **kwargs):
        print("Creating BeamNG simulation in simulator")
        self.scenario_number += 1
        return BeamNGSimulation(scene, self.bng, self.scenario, self.scenario_number, timestep=self.timestep, **kwargs)

        
    def destroy(self):
        self.bng.close()
        super().destroy()


class BeamNGSimulation(DrivingSimulation):
    def __init__(self, scene, bng: BeamNGpy, scenario: Scenario, scenario_number, **kwargs):
        self.bng = bng
        self.scenario = scenario
        self.scenario_number = scenario_number

        super().__init__(scene, **kwargs)

    def setup(self):
        super().setup()  # Calls createObjectInSimulator for each object
        return
    
    def createObjectInSimulator(self, obj):
        # can only spawn vehicles for now
        try:
            vehicle = Vehicle(obj.vid, obj.model, license=obj.vid)
            p = utils.scenicToBeamNGVector(obj.position)
            print("spawned vehicle at", p)
            rot_quat = utils.euler_to_quaternion(obj.yaw, obj.pitch, obj.roll)
            print("rot quat", rot_quat)
            self.scenario.add_vehicle(vehicle, pos=p, rot_quat=rot_quat)
            print("Added vehicle to scenario")
        except Exception as e:
            raise SimulationCreationError(f"Failed to spawn object {obj} in simulator") from e

    def executeActions(self, allActions):
        for agent, actions in allActions.items():
            for action in actions:
                action.applyTo(agent, self)
        return
    
    def step(self):
        self.bng.control.step(1)
        
    def getProperties(self, obj, properties):
        self.scenario.update()
        vehicle = self.scenario.get_vehicle(obj.vid)
        imu = AdvancedIMU(f'imu_{obj.vid}', self.bng, vehicle, gfx_update_time=self.timestep, 
                          is_send_immediately=True)
        poll = imu.poll()
        
        if poll:
            angularVelocity = utils.beamNGToScenicVector(poll['angVel'])
            angularSpeed = math.hypot(*angularVelocity)
        else:
            angularVelocity = Vector(0, 0, 0)
            angularSpeed = 0
        position = utils.beamNGToScenicVector(vehicle.state['pos'])
        direction = vehicle.state['dir']
        up = vehicle.state['up']
        velocity = utils.beamNGToScenicVector(vehicle.state['vel'])
        speed = math.hypot(*velocity)

        yaw, pitch, roll = utils.quaternion_to_euler(vehicle.state['rotation'])

        values = dict(
                    position=position,
                    yaw=yaw,
                    pitch=pitch,
                    roll=roll,
                    velocity=velocity,
                    speed=speed,
                    angularSpeed=angularSpeed,
                    angularVelocity=angularVelocity,
                )
        
        return values

    def destroy(self):
        pass