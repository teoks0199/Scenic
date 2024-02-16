from abc import ABC, abstractmethod
import enum
from pathlib import Path
import time

import rv_ltl
import scipy

from scenic.contracts.contracts import ContractEvidence, ContractResult
from scenic.contracts.utils import linkSetBehavior, lookuplinkedObject
from scenic.core.distributions import RejectionException
from scenic.core.dynamics import GuardViolation, RejectSimulationException
from scenic.core.scenarios import Scenario


class Testing:
    def __init__(
        self,
        ## Testing Specific ##
        confidence,
        batchSize,
        verbose,
        ## Compiler Provided ##
        contract,
        component,
        obj,
        termConditions,
        reqConditions,
    ):
        # Store general args
        self.confidence = confidence
        self.batchSize = batchSize
        self.verbose = verbose
        self.contract = contract
        self.component = component
        self.obj = obj
        self.termConditions = termConditions
        self.reqConditions = reqConditions

    def verify(self):
        evidence = self._newEvidence()
        result = ProbabilisticContractResult(
            self.contract.assumptions, self.contract.guarantees, evidence
        )

        activeTermConditions = (
            self.termConditions if self.termConditions else self.reqConditions
        )

        while not any(
            cond.check(evidence) for cond in self.termConditions + self.reqConditions
        ):
            evidence.addTests(self.runTests(self.batchSize))

            if self.verbose:
                print(result)
                print()

        if self.verbose and self.termConditions:
            print("Termination Conditions:")
            for cond in self.termConditions:
                print(f"  {cond} = {cond.check(evidence)}")
            print()

        # Check requirements
        evidence.requirementsMet = all(
            cond.check(evidence) for cond in self.reqConditions
        )

        if self.verbose and self.reqConditions:
            print("Requirement Conditions:")
            for cond in self.reqConditions:
                print(f"  {cond} = {cond.check(evidence)}")
            print()

        return result

    @abstractmethod
    def _newEvidence(self):
        raise NotImplementedError()


class SimulationTesting(Testing):
    def __init__(
        self,
        scenario,
        maxSteps,
        *,
        ## Testing Specific ##
        confidence=0.95,
        batchSize=1,
        verbose=False,
        ## Compiler Provided ##
        contract,
        component,
        obj,
        termConditions,
        reqConditions,
    ):
        super().__init__(
            confidence=confidence,
            batchSize=batchSize,
            verbose=verbose,
            contract=contract,
            component=component,
            obj=obj,
            termConditions=termConditions,
            reqConditions=reqConditions,
        )

        # Store technique specific args
        self.scenario = scenario
        self.maxSteps = maxSteps

        assert len(termConditions) + len(reqConditions) > 0

    def _newEvidence(self):
        return SimulationEvidence(self.confidence, self.scenario)

    @staticmethod
    def _createTestData(result, violations, scenario, scene, simulation, start_time):
        return SimulationTestData(
            result,
            violations,
            scenario.sceneToBytes(scene),
            simulation.getReplay(),
            time.time() - start_time,
        )

    def runTests(self, num_tests):
        # Generate scenes
        scenes, _ = self.scenario.generateBatch(numScenes=num_tests)

        # Evaluate each scene
        tests = []
        for scene in scenes:
            tests.append(self.testScene(scene))

        return tests

    def testScene(self, scene):
        start_time = time.time()

        # Link object
        linkSetBehavior(scene, [self.obj])

        ## Create and link EagerValueWindows ##
        base_value_windows = {}
        # Objects
        assert len(self.contract.objects) == 1
        object_name = self.contract.objects[0]
        obj_ptr = lookuplinkedObject(scene, self.component.linkedObjectName)
        base_value_windows[object_name] = EagerValueWindow((lambda: obj_ptr))

        # Globals
        for global_name in self.contract.globals:
            if global_name == "objects":
                objects_ptr = scene.objects
                base_value_windows[global_name] = EagerValueWindow((lambda: objects_ptr))
            elif global_name == "WORKSPACE":
                workspace_ptr = scene.workspace
                base_value_windows[global_name] = EagerValueWindow(
                    (lambda: workspace_ptr)
                )
            else:
                raise ValueError(f"Unrecognized global value '{global_name}'")

        # Inputs
        for input_name in self.contract.inputs_types.keys():
            base_value_windows[input_name] = EagerValueWindow(
                (lambda: self.component.last_inputs[input_name])
            )

        # Outputs
        for output_name in self.contract.outputs_types.keys():
            base_value_windows[output_name] = EagerValueWindow(
                (lambda: self.component.last_outputs[output_name])
            )

        value_windows = {**base_value_windows}

        # Definitions
        for def_name, def_lambda in self.contract.definitions.items():
            def_closure = lambda l, x: lambda t: l(t, *x.values())
            value_windows[def_name] = LazyValueWindow(
                def_closure(def_lambda, value_windows.copy())
            )

        ## Create Monitors for Assumptions/Guarantees
        assumptions_monitors = [a.create_monitor() for a in self.contract.assumptions]
        assumptions_values = [
            rv_ltl.B4.PRESUMABLY_TRUE for a in self.contract.assumptions
        ]
        guarantees_monitors = [g.create_monitor() for g in self.contract.guarantees]
        guarantees_values = [rv_ltl.B4.PRESUMABLY_TRUE for g in self.contract.guarantees]

        ## Evaluate Contract on Simulation ##
        sim_step = 0
        eval_step = 0

        # Instantiate simulator
        simulator = self.scenario.getSimulator()

        # Step contract till termination
        with simulator.simulateStepped(scene, maxSteps=self.maxSteps) as simulation:
            print(self.contract.max_lookahead)
            # Populate with lookahead values
            for _ in range(self.contract.max_lookahead):
                # Advance simulation one time step, catching any rejections
                try:
                    simulation.advance()
                except (
                    RejectSimulationException,
                    RejectionException,
                    GuardViolation,
                ) as e:
                    return self._createTestData(
                        TestResult.R, [], self.scenario, scene, simulation, start_time
                    )

                # If the simulation finished, move on.
                if simulation.result:
                    break

                # Update all base value windows
                for vw_name, vw in base_value_windows.items():
                    vw.update()

                sim_step += 1

            # Run remaining simulation
            while eval_step <= sim_step:
                # If simulation not terminated, advance simulation one time step, catching any rejections
                if not simulation.result:
                    try:
                        simulation.advance()
                    except (
                        RejectSimulationException,
                        RejectionException,
                        GuardViolation,
                    ) as e:
                        return self._createTestData(
                            TestResult.R, [], self.scenario, scene, simulation, start_time
                        )

                    # If the simulation didn't finish, update value windows
                    if not simulation.result:
                        # Update all base value windows
                        for vw_name, vw in base_value_windows.items():
                            vw.update()

                        # Increment simulation step
                        sim_step += 1

                print(value_windows["lead_dist"].window)

                # Check all assumptions and guarantees
                prop_params = [eval_step] + list(value_windows.values())
                for a_iter, assumption in enumerate(assumptions_monitors):
                    try:
                        a_val = assumption.update(prop_params)
                        assumptions_values[a_iter] = a_val
                    except InvalidTimeException as e:
                        if e.time < sim_step and simulation.result:
                            raise

                # If we've definitely violated an assumption, we can terminate early.
                violated_assumptions = [
                    ai
                    for ai, av in enumerate(assumptions_values)
                    if av == rv_ltl.B4.FALSE
                ]

                if violated_assumptions and False:
                    return self._createTestData(
                        TestResult.A,
                        violated_assumptions,
                        self.scenario,
                        scene,
                        simulation,
                        start_time,
                    )

                for g_iter, guarantee in enumerate(guarantees_monitors):
                    try:
                        r_val = guarantee.update(prop_params)
                        guarantees_values[g_iter] = r_val
                    except InvalidTimeException as e:
                        if e.time < sim_step and simulation.result:
                            raise

                # Increment evaluation step
                eval_step += 1

        # Check final status assumptions and guarantees
        violated_assumptions = [
            ai
            for ai, av in enumerate(assumptions_values)
            if av == rv_ltl.B4.PRESUMABLY_FALSE or av == rv_ltl.B4.FALSE
        ]
        if violated_assumptions:
            return self._createTestData(
                TestResult.A,
                violated_assumptions,
                self.scenario,
                scene,
                simulation,
                start_time,
            )

        violated_guarantees = [
            gi
            for gi, gv in enumerate(guarantees_values)
            if gv == rv_ltl.B4.PRESUMABLY_FALSE or gv == rv_ltl.B4.FALSE
        ]
        if len(violated_guarantees) > 0:
            return self._createTestData(
                TestResult.G,
                violated_guarantees,
                self.scenario,
                scene,
                simulation,
                start_time,
            )
        else:
            return self._createTestData(
                TestResult.V, [], self.scenario, scene, simulation, start_time
            )


class EagerValueWindow:
    def __init__(self, get_val):
        self.elapsed_time = 0
        self.get_val = get_val
        self.window = []

    def update(self):
        new_val = self.get_val()
        self.elapsed_time += 1
        self.window.append(new_val)

    def __getitem__(self, time):
        if not time < self.elapsed_time:
            raise InvalidTimeException(time)

        return self.window[time]


class LazyValueWindow:
    def __init__(self, get_val):
        self.elapsed_time = 0
        self.get_val = get_val
        self.window = {}

    def update(self, time):
        self.window[time] = self.get_val(time)
        self.elapsed_time += max(self.elapsed_time, time)

    def __getitem__(self, time):
        if time not in self.window:
            self.update(time)

        return self.window[time]


class InvalidTimeException(Exception):
    def __init__(self, time):
        self.time = time


## Test Data Classes
@enum.unique
class TestResult(enum.Enum):
    V = "Valid: The contract was successfully validated"
    R = "Rejected: The scenario was rejected or a guard was violated"
    A = "Assumptions: An assumption was violated"
    G = "Guarantees: A guarantee was violated"


class TestData:
    def __init__(self, result, violations, elapsed_time):
        self.result = result
        self.violations = violations
        self.elapsed_time = elapsed_time


class SimulationTestData(TestData):
    def __init__(self, result, violations, scene_bytes, sim_replay, elapsed_time):
        super().__init__(result, violations, elapsed_time)
        self.scene_bytes = scene_bytes
        self.sim_replay = sim_replay


class ProbabilisticEvidence(ContractEvidence, ABC):
    def __init__(self, confidence):
        assert self.source_hash

        self.confidence = confidence
        self.testData = []
        self.requirementsMet = None

        # Initialize metrics
        self.elapsed_time = 0
        self.v_count = 0
        self.r_count = 0
        self.a_count = 0
        self.g_count = 0

    def addTests(self, newTests):
        # Update metrics
        self.elapsed_time += sum(t.elapsed_time for t in newTests)
        self.v_count += len(list(filter(lambda t: t.result == TestResult.V, newTests)))
        self.r_count += len(list(filter(lambda t: t.result == TestResult.R, newTests)))
        self.a_count += len(list(filter(lambda t: t.result == TestResult.A, newTests)))
        self.g_count += len(list(filter(lambda t: t.result == TestResult.G, newTests)))

        # Add new tests
        self.testData += newTests

    @property
    def confidenceGap(self):
        if len(self) == 0 or (self.v_count + self.g_count) == 0:
            return 1

        bt = scipy.stats.binomtest(k=self.v_count, n=self.v_count + self.g_count)
        ci = bt.proportion_ci(confidence_level=self.confidence)
        return ci.high - ci.low

    @property
    def meanCorrectness(self):
        if self.v_count + self.g_count == 0:
            return float("nan")

        return self.v_count / (self.v_count + self.g_count)

    @property
    def correctness(self):
        if self.v_count + self.g_count == 0:
            return 0

        bt = scipy.stats.binomtest(
            k=self.v_count, n=self.v_count + self.g_count, alternative="greater"
        )
        ci = bt.proportion_ci(confidence_level=self.confidence)
        return ci.low

    @property
    @abstractmethod
    def _source_info(self):
        raise NotImplementedError()

    def __len__(self):
        return len(self.testData)

    def __iter__(self):
        return self.testData

    def __str__(self):
        string = (
            f"Probabilistic Evidence\n"
            f"{100*self.correctness:.2f}% Correctness with {100*self.confidence:.2f}% Confidence\n"
            f"Sampled from {self._source_info}\n"
            f"{self.v_count} Verified,  {self.r_count} Rejected,  "
            f"{self.a_count} A-Violated,  {self.g_count} G-Violated\n"
            f"{len(self.testData)} Samples, {self.elapsed_time:.2f} Seconds\n"
            f"Mean Correctness: {100*self.meanCorrectness:.2f}%\n"
            f"Confidence Gap: {self.confidenceGap:.4f}"
        )
        return string


class SimulationEvidence(ProbabilisticEvidence):
    def __init__(self, confidence, source):
        # Validate and store source
        if not isinstance(source, Scenario):
            raise ValueError("SimulationEvidence must have a Scenario object as a source")

        self.source_filename = source.filename
        self.source_hash = source.astHash

        super().__init__(confidence)

    def addTests(self, newTests):
        if any(not isinstance(t, SimulationTestData) for t in newTests):
            raise ValueError(
                "SimulationEvidence can only accept tests of class SimulationTestData"
            )

        super().addTests(newTests)

    @property
    def _source_info(self):
        return f"Scenario '{Path(self.source_filename).name}' (Hash={int.from_bytes(self.source_hash)})"


class ProbabilisticContractResult(ContractResult):
    def __init__(self, assumptions, guarantees, evidence):
        if not isinstance(evidence, ProbabilisticEvidence):
            raise ValueError("Evidence provided is not ProbabilisticEvidence")

        super().__init__(assumptions, guarantees, evidence)

    def __str__(self):
        string = "ContractResult:\n"
        string += "  Assumptions:\n"

        for ai, a in enumerate(self.assumptions):
            if self.evidence.a_count == 0:
                percent_violated = 0
            else:
                percent_violated = (
                    sum(
                        1 / len(at.violations)
                        for at in self.evidence.testData
                        if at.result == TestResult.A and ai in at.violations
                    )
                    / self.evidence.a_count
                )

            string += f"    ({percent_violated*100:6.2f}%) {a}\n"

        string += "  Guarantees:\n"

        for gi, g in enumerate(self.guarantees):
            if self.evidence.g_count == 0:
                percent_violated = 0
            else:
                percent_violated = (
                    sum(
                        1 / len(gt.violations)
                        for gt in self.evidence.testData
                        if gt.result == TestResult.G and gi in gt.violations
                    )
                    / self.evidence.g_count
                )

            string += f"    ({percent_violated*100:6.2f}%) {g}\n"

        string += f"  Evidence: \n"
        string += "    " + str(self.evidence).replace("\n", "\n    ")
        return string


## Termination/Requirement Conditions
class Condition(ABC):
    @abstractmethod
    def check(self, evidence):
        raise NotImplementedError()

    def __str__(self):
        return repr(self)


class TimeTerminationCondition(Condition):
    def __init__(self, timeout):
        self.timeout = timeout

    def check(self, evidence):
        return evidence.elapsed_time >= self.timeout

    def __repr__(self):
        return f"{self.__class__.__name__}({self.timeout})"


class CountTerminationCondition(Condition):
    def __init__(self, count):
        self.count = count

    def check(self, evidence):
        return len(evidence) >= self.count

    def __repr__(self):
        return f"{self.__class__.__name__}({self.count})"


class GapTerminationCondition(Condition):
    def __init__(self, gap):
        self.gap = gap

    def check(self, evidence):
        return evidence.confidenceGap <= self.gap

    def __repr__(self):
        return f"{self.__class__.__name__}({self.gap})"


class CorrectnessRequirementCondition(Condition):
    def __init__(self, correctness):
        self.correctness = correctness

    def check(self, evidence):
        return evidence.correctness >= self.correctness

    def __repr__(self):
        return f"{self.__class__.__name__}({self.correctness})"
