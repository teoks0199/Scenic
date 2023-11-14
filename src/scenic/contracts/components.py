from abc import ABC, abstractmethod
import graphlib
import warnings

from scenic.core.dynamics.actions import Action
from scenic.core.specifiers import Specifier


class Component(ABC):
    pass


class BaseComponent(Component):
    def __init__(self, **kwargs):
        # Extract linked Scenic object, if one exists.
        assert "_SCENIC_INTERNAL_LINKED_OBJ_NAME" in kwargs
        self.linkedObjectName = kwargs["_SCENIC_INTERNAL_LINKED_OBJ_NAME"]
        del kwargs["_SCENIC_INTERNAL_LINKED_OBJ_NAME"]

        # Save args
        self.kwargs = kwargs

        # Ensure that all input/output types are actually types
        for input_type in self.inputs_types.values():
            assert isinstance(input_type, type)
        for output_type in self.outputs_types.values():
            assert isinstance(output_type, type)

        # Initialize state
        self.reset()

    def link(self, scene):
        self.linkedObject = lookuplinkedObject(scene, self.linkedObjectName)

    def reset(self):
        self.linkedObject = None
        self.state = ComponentState(self.state_types)

        for name, val in self.state_inits.items():
            setattr(self.state, name, val)

    def run(self, inputs):
        # Check validity of inputs
        assert isinstance(inputs, dict) and set(inputs.keys()) == set(
            self.inputs_types.keys()
        )
        for input_name, input_val in inputs.items():
            assert isinstance(input_val, self.inputs_types[input_name])

        # Extract sensor values and check validity
        sensors = {}
        for sensor_name, sensor_source in self.sensors_values.items():
            assert sensor_source[1] == "self"
            assert hasattr(self.linkedObject, sensor_source[0])
            sensor_val = getattr(self.linkedObject, sensor_source[0])
            assert isinstance(sensor_val, self.sensors_types[sensor_name])
            sensors[sensor_name] = sensor_val

        # Run component to get outputs
        outputs = self.run_inner(
            self.state, *inputs.values(), *sensors.values(), **self.kwargs
        )

        # Check validity of outputs
        assert isinstance(outputs, dict) and set(outputs.keys()) == set(
            self.outputs_types.keys()
        )
        for output_name, output_val in outputs.items():
            assert isinstance(output_val, self.outputs_types[output_name])

        return (outputs, [])

    @staticmethod
    @abstractmethod
    def run_inner():
        pass


class ActionComponent(Component):
    def __init__(self, **kwargs):
        # Extract linked Scenic object, if one exists.
        assert "_SCENIC_INTERNAL_LINKED_OBJ_NAME" in kwargs
        self.linkedObjectName = kwargs["_SCENIC_INTERNAL_LINKED_OBJ_NAME"]
        del kwargs["_SCENIC_INTERNAL_LINKED_OBJ_NAME"]

        # Save args
        self.kwargs = kwargs

        # Ensure that all action types are actually types
        for action_type in self.inputs_types.values():
            assert isinstance(action_type, type)
            assert issubclass(action_type, Action)

        # Initialize state
        self.reset()

    def link(self, scene):
        self.linkedObject = lookuplinkedObject(scene, self.linkedObjectName)

    def reset(self):
        self.linkedObject = None

    def run(self, actions):
        for action_name, action in actions.items():
            assert action_name in self.inputs_types
            assert isinstance(action, self.inputs_types[action_name])

        return ({}, list(actions.values()))


class ComposeComponent(Component):
    def __init__(self, **kwargs):
        # Extract linked Scenic object, if one exists.
        assert "_SCENIC_INTERNAL_LINKED_OBJ_NAME" in kwargs
        self.linkedObjectName = kwargs["_SCENIC_INTERNAL_LINKED_OBJ_NAME"]
        del kwargs["_SCENIC_INTERNAL_LINKED_OBJ_NAME"]

        # Save args
        self.kwargs = kwargs

        # Ensure that all input/output types are actually types
        for input_type in self.inputs_types.values():
            assert isinstance(input_type, type)
        for output_type in self.outputs_types.values():
            assert isinstance(output_type, type)

        # Ensure that all subcomponent are actually components
        for sc in self.subcomponents.values():
            assert isinstance(sc, Component)

        # Validate and construct component dataflow graph
        self.dataflow_graph = {node: [] for node in self.subcomponents.keys()}
        self.dataflow_graph["SELF_INPUT"] = []
        self.dataflow_graph["SELF_OUTPUT"] = []
        self.input_sources = {}
        for source, target in self.connections:
            # Extract parent components for source and target and check compatibility
            if source[1] is None:
                source_parent = "SELF_INPUT"
                assert source[0] in self.inputs_types.keys()
                source_type = self.inputs_types[source[0]]
            else:
                assert source[1] in self.subcomponents
                source_parent = source[1]
                assert source[0] in self.subcomponents[source[1]].outputs_types.keys()
                source_type = self.subcomponents[source[1]].outputs_types[source[0]]

            if target[1] is None:
                target_parent = "SELF_OUTPUT"
                assert target[0] in self.outputs_types.keys()
                target_type = self.outputs_types[target[0]]
            else:
                assert target[1] in self.subcomponents
                target_parent = target[1]
                assert target[0] in self.subcomponents[target[1]].inputs_types.keys()
                target_type = self.subcomponents[target[1]].inputs_types[target[0]]

            # Add edge to dataflow graph
            self.dataflow_graph[target_parent].append((source_parent))

            # Log source of this input
            self.input_sources[(target[0], target_parent)] = (source[0], source_parent)

        # Ensure all source ports have a source
        for output_name in self.outputs_types.keys():
            assert (output_name, "SELF_OUTPUT") in self.input_sources

        for sc_name, sc_val in self.subcomponents.items():
            for input_name in self.subcomponents[sc_name].inputs_types.keys():
                assert (input_name, sc_name) in self.input_sources

        # TODO: Raise a warning if any of this component's inputs are not used.

        # Find valid component evaluation order or raise error
        sorter = graphlib.TopologicalSorter(self.dataflow_graph)
        self.evaluation_order = [
            sc for sc in sorter.static_order() if sc not in {"SELF_INPUT", "SELF_OUTPUT"}
        ]

    def link(self, scene):
        self.linkedObject = lookuplinkedObject(scene, self.linkedObjectName)
        for sc in self.subcomponents.values():
            sc.link(scene)

    def reset(self):
        self.linkedObject = None
        for sc in self.subcomponents.values():
            sc.reset()

    def run(self, inputs):
        # Check validity of inputs
        assert isinstance(inputs, dict) and set(inputs.keys()) == set(
            self.inputs_types.keys()
        )
        for input_name, input_val in inputs.items():
            assert isinstance(input_val, self.inputs_types[input_name])

        # Initialize actions list/values dictionary and load in inputs
        actions = []
        values = {
            (input_name, "SELF_INPUT"): input_val
            for input_name, input_val in inputs.items()
        }

        # Run all subcomponents
        for sc_name in self.evaluation_order:
            # Extract the subcomponent and its input values
            sc = self.subcomponents[sc_name]
            sc_inputs = {
                input_name: values[self.input_sources[(input_name, sc_name)]]
                for input_name in sc.inputs_types.keys()
            }

            # Run the subcomponent and process the result
            sc_outputs, sc_actions = sc.run(sc_inputs)
            values.update(
                {
                    (sc_output_name, sc_name): sc_output_val
                    for sc_output_name, sc_output_val in sc_outputs.items()
                }
            )
            actions += sc_actions

        # Extract and check validity of outputs
        values.update(
            {
                (output_name, "SELF_OUTPUT"): values[
                    self.input_sources[(output_name, "SELF_OUTPUT")]
                ]
                for output_name in self.outputs_types.keys()
            }
        )
        outputs = {
            name[0]: val for name, val in values.items() if name[1] == "SELF_OUTPUT"
        }

        assert isinstance(outputs, dict) and set(outputs.keys()) == set(
            self.outputs_types.keys()
        )
        for output_name, output_val in outputs.items():
            assert isinstance(output_val, self.outputs_types[output_name])

        return outputs, actions


## Component state
class ComponentState:
    def __init__(self, state_types):
        object.__setattr__(self, "_state_types", {n: t for n, t in state_types.items()})

    def __getattr__(self, name):
        if name not in self._state_types.keys():
            raise ValueError(f"Attempted to access non-existant state variable '{name}'.")

        return object.__getattribute__(self, name)

    def __setattr__(self, name, value):
        if name not in self._state_types.keys():
            raise ValueError(f"Attempted to set non-existant state variable '{name}'.")

        if not isinstance(value, self._state_types[name]):
            raise ValueError(
                f"Attempted to set state variable '{name}' to {value} of type {type(value)}."
            )

        object.__setattr__(self, name, value)


# Component behavior
class ComponentBehavior:
    def __init__(self, behavior):
        assert len(behavior.inputs_types) == 0
        self.behavior = behavior
        self._agent = None
        self._isRunning = False

    def _assignTo(self, agent):
        if self._agent and agent is self._agent._dynamicProxy:
            # Assigned again (e.g. by override) to same agent; do nothing.
            return
        self._start(agent)

    def _start(self, agent):
        self._agent = agent
        self._isRunning = True

    def _step(self):
        _, actions = self.behavior.run({})
        return tuple(actions)

    def _stop(self, reason=None):
        self._agent = None
        self._isRunning = False


# Utility functions
def lookuplinkedObject(scene, name):
    target_objects = [
        obj for obj in scene.objects if hasattr(obj, "name") and obj.name == name
    ]

    if len(target_objects) == 0:
        raise RuntimeError(f"No object in scenario with name '{name}'")

    if len(target_objects) > 1:
        raise RuntimeError(f"Multiple objects in scenario with name '{name}'")

    return target_objects[0]


def runComponentsSimulation(scenario, components, time=200):
    # Generate a scene and override component behaviors.
    scene, _ = scenario.generate()

    for component in components:
        component.link(scene)

        if component.linkedObject.behavior:
            warnings.warn(
                f"Overriding behavior of {component.linkedObjectName} with component behavior."
            )

        component.linkedObject._override(
            [
                Specifier(
                    "ComponentBehaviorOverride",
                    {"behavior": 1},
                    {"behavior": ComponentBehavior(component)},
                )
            ]
        )

    # Instantiate simulator and run simulation
    simulator = scenario.getSimulator()

    simulation = simulator.simulate(scene, maxSteps=time)

    # Reset components
    for component in components:
        component.reset()