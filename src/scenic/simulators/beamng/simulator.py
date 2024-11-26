"""Simulator interface for beamNG."""

"""
Introduction to Simulator Interface
This file illustrates the basics on how to 
implement the Simultor and Simulation class for your
Scenic interface. The docstrings in each function
and class gives a brief description on what you should
write in each function and gives examples where needed.
"""
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
    """
    Implementation of `Simulator` in scenic.core.simulator.
    At each simulation, Simulator creates a Simulation class
    The Simulation class then runs the actual simulation.
    The core methods that need to be implemented/modified in this class are:
        __init__
        createSimulation
        destroy
    See their respective docstrings for details and how to fill them out.
    The rough execution flow in the background for a n-iteration Scenic run is:
        while number_of_simulations <= n:
            simulation = self.createSimulation()
            run_simulation(simulation)
            number_of_simulations += 1
        self.destory()
    see the Scenic docs and scenic.core.simulator for more details.
    """

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
        """
        You can put anything you want in __init__ here, as long as super().__init__() is called.
        Keyword arguments can be added to the signature to set up some desired field, such as the
        size of the simulation timestep
        
        Example 1:
            def __init__(self, timestep=0):
                self.timestep = timestep
                super().__init__()
        Example 2:
            def __init__(self):
                YourSimulatorAPI.turn_on_simulator()
                super().__init__()
        """
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
        """
        There is no required code here other than super().destory()
        You can add code does post-processing of the simulation output
        or code that turns of the simulator here
        Example 1:
            def destroy(self):
                YourSimulatorAPI.turn_off_simulator()
                super().destory()
        Example 2:
            def destroy(self):
                YourSimulatorAPI.save_simulation_recordings()
                super().destory()
        """
        self.bng.close()
        super().destroy()


class BeamNGSimulation(DrivingSimulation):
    """
    Implementation of the Simulation class in scenic.core.simulator
    This class is responsible for:
        1. Running the simulation
        2. Creating the simulation world according to the Scenic program
        3. Passing on Scenic's commands to control the agents to the simulator
        4. Obtaining the world state information from the simulator and passing
           it back to Scenic
    Core Methods to implement/modify:
        1. __init__
        2. setup
        3. createObjectInSimulator
        4. executeActions
        5. step
        6. getProperties
        7. destroy
    See their respective docstrings for details and how to fill them out.
    NOTE: createObjectInSimulator() is already called for you for each object in super().setup()
    The rough execution flow when running a simulation is as follows:
        self.setup() # calls createObjectInSimulator inside
        while simulation is running:
            self.executeActions()
            self.step()
            self.getProperties()
        self.destroy()
    See the Simulation class in scenic.core.simulator for more details
    """

    def __init__(self, scene, bng: BeamNGpy, scenario: Scenario, scenario_number, **kwargs):
        print("Creating BeamNG simulation")

        self.bng = bng
        self.scenario = scenario
        self.scenario_number = scenario_number

        super().__init__(scene, **kwargs)

    def setup(self):
        super().setup()  # Calls createObjectInSimulator for each object
        return
    
    def createObjectInSimulator(self, obj):
        """
        Arg
        Object obj: a Scenic obj/agent
        Spawns a single object/agent in the simulator
        with the desired parameters (position, orientation, color, etc.)
        Example:
            Note that when you fail to spawn an object, you should
            raise a SimulationCreationError
            def createObjectInSimulator(self, obj):
                if <obj is a Car>:
                    try:
                        YourSimulatorAPI.spawn_car(
                                        position = obj.position,
                                        orientation = obj.yaw,
                                        color = obj.color,
                                        model = obj.modelx
                        )
                    except:
                        raise SimulationCreationError("spawn objec failed")
                else:
                    try:
                        YourSimulatorAPI.spawn_object(
                                        position = obj.position 
                                        orientation = obj.yaw
                        )
                    except:
                        raise SimulationCreationError("spawn objec failed")
        """
        try:
            vehicle = Vehicle(obj.vid, obj.model, license=obj.vid)
            p = utils.scenicToBeamNGVector(obj.position)
            p = (obj.pos)
            print("spawned vehicle at", p)
            self.scenario.add_vehicle(vehicle, pos=p)
            print("Added vehicle to scenario")
        except Exception as e:
            raise SimulationCreationError(f"Failed to spawn object {obj} in simulator") from e

    def executeActions(self, allActions):
        """
        Args:
        allActions: a :obj:`~collections.defaultdict` mapping each agent to a tuple
                        of actions, with the default value being an empty tuple. The order of
                        agents in the dict should be respected in case the order of actions matters.
        Iterates through all the Scenic Actions to be carried out for all the agents.
        For each Scenic Action, this function calls the applyTo() method of the Action's class
        as defined in actions.py.
        Note that typically, when calling applyTo(), we do not actually render the physics of the action.
        That is, the action command is sent, but the world remains frozen.
        The action only gets carried out when we call step(), where the world unfreezes and
        the simulation physics is advanced by one timestep.
        Example 1:
            This is the implementation if you call super().executeActions(allActions)
            for agent, actions in allActions.items():
                for action in actions:
                    action.applyTo(agent, self)
            return
        Example 2:
            You can implement your Action.applyTo() to return something.
            The following is an example where the applyTo() returns a function that,
            when called in step(), execute the Action and renders it in simulation
            
            self.step_action_buffer = []
            for agent, actions in allActions.items():
                for action in actions:
                    a = action.applyTo(agent, self)
            self.step_action_buffer.append(a)
            return
            Where we will iterate through the step_action_buffer in step()
            and call each function like this:
            def step(self):
                for a in self.step_action_buffer:
                    a()
        """
        for agent, actions in allActions.items():
            for action in actions:
                action.applyTo(agent, self)
        return
    
    def step(self):
        self.bng.control.step(1)
        
    def getProperties(self, obj, properties):
        """
        Args:
        obj (Object): Scenic object in question.

        properties (set): Set of names of properties to read from the simulator.
        It is safe to destructively iterate through the set if you want.
        Returns:
        values (dict): A dictionary that with the property names as keys
        that returns the current value of the property
        Obtains the current values for each Scenic agent/object's properties
        such as current position, orientation, speed, etc. 
        There are certain properties that you have to obtain for all objects.
        The 'values' dictionary in Example 1 below contains these core properties.
        If any of these core properties does not apply to you or does not matter,
        feel free to always set them to 0 (like with pitch and roll values in Example 1)
        Example 1:
            def getProperties(self, obj, properties)
                position = YourSimulatorAPI.get_position(obj.id)
                yaw = YourSimulatorAPI.get_orientation(obj.id)
                velocity = YourSimulatorAPI.get_velocity(obj.id)
                etc etc ...
                values = dict(
                    position=position,
                    yaw=yaw,
                    pitch=0,
                    roll=0,
                    velocity=velocity,
                    speed=speed,
                    angularSpeed=angularSpeed,
                    angularVelocity=angularVelocity,
                )
        Example 2 (from the Newtonian simulator interface):
            
            You can also update properties unique to each object class 
            like how we update the 'elevation' property below
            def getProperties(self, obj, properties):
                yaw, _, _ = obj.parentOrientation.globalToLocalAngles(obj.heading, 0, 0)
                values = dict(
                    position=obj.position,
                    yaw=yaw,
                    pitch=0,
                    roll=0,
                    velocity=obj.velocity,
                    speed=obj.speed,
                    angularSpeed=obj.angularSpeed,
                    angularVelocity=obj.angularVelocity,
                )
                if "elevation" in properties:
                    values["elevation"] = obj.elevation
                return values
        Example 3:
            You can also update non-core properties without using the values dictionary,
            like what we do with the obj.camera_observation below
            
             
            position = YourSimulatorAPI.get_position(obj.id)
            yaw = YourSimulatorAPI.get_orientation(obj.id)
            velocity = YourSimulatorAPI.get_velocity(obj.id)
            etc etc ...
            def getProperties(self, obj, properties):
                values = dict(
                    position=position,
                    yaw=yaw,
                    pitch=0,
                    roll=0,
                    velocity=obj.velocity,
                    speed=obj.speed,
                    angularSpeed=obj.angularSpeed,
                    angularVelocity=obj.angularVelocity,
                )
                camera_observation = YourSimulatorAPI.get_camera_observation(obj.id)
                obj.camear_observation.append(camera_observation)
                return values
        """
        
        self.scenario.update()
        #print("vid", obj.vid)
        vehicle = self.scenario.get_vehicle(obj.vid)
        imu = AdvancedIMU(f'imu_{obj.vid}', self.bng, vehicle, gfx_update_time=self.timestep, 
                          is_send_immediately=True)
        poll = imu.poll()
        #print(poll)
        
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
        """
        You should delete/destroy/unspawn objects created by Scenic here when needed.
        Data processing at the end of simulation can also be done here.
        Scenic 3.0.0, super().destroy() does nothing and can be overridden
        Example 1:
        You can always use the self.objects field, inherited from the 
        Simulation class from scenic.core.simulator, to access the objects/agents
        spawned by Scenic
            def destroy(self):
                for obj in self.objects:
                    if obj is Robot:
                        YourSimulatorAPI.shut_down_robot(obj.robot_id)
                        YourSimulatorAPI.delete_robot(obj.robot_id)
                    else:
                        YourSimulatorAPI.delete_object(obj.object_id)
                # Making videos of the simulation, assuming self.observations
                # contains the observations we have made throughout the simulation
                video_save_path = your/video/save/path/
                YourSimulatorAPI.make_video(self.observations, path=video_save_path + "video_1.mp4")
                return
        """
        pass