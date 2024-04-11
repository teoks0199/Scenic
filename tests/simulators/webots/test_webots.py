import os
import subprocess

import pytest

from tests.utils import pickle_test, sampleScene, tryPickling

WEBOTS_BINARY_PATH = "/usr/local/bin/webots"
WEBOTS_RESULTS_FILE_PATH = f"{os.path.dirname(__file__)}/dynamic/results.txt"
WEBOTS_WORLD_FILE_PATH = (
    f"{os.path.dirname(__file__)}/dynamic/webots_data/worlds/world.wbt"
)


def receive_results():
    with open(WEBOTS_RESULTS_FILE_PATH, "r") as file:
        content = file.read()
    return content


def cleanup_results():
    command = f"rm -f {WEBOTS_RESULTS_FILE_PATH}"
    subprocess.run(command, shell=True)


def test_dynamics_scenarios(webotsAvailable):
    webotsAvailable(WEBOTS_BINARY_PATH)
    cleanup_results()
    command = (
        f"bash {WEBOTS_BINARY_PATH} --no-rendering --minimize {WEBOTS_WORLD_FILE_PATH}"
    )
    subprocess.run(command, shell=True)
    data = receive_results()
    assert data != None
    start_z = float(data.split(",")[1].strip(" )]"))
    end_z = float(data.split(",")[3].strip(" )]"))
    assert start_z == 0.5
    assert start_z > end_z
    expected_value = 0.09
    tolerance = 0.01
    assert end_z == pytest.approx(expected_value, abs=tolerance)


def test_webots_available_fixture(webotsAvailable):
    with pytest.raises(pytest.skip.Exception):
        webotsAvailable(WEBOTS_BINARY_PATH + "/foo")


def test_receive_results():
    command = f"echo 'Hello, world!' >> {WEBOTS_RESULTS_FILE_PATH}"
    subprocess.run(command, shell=True)
    data = receive_results()
    assert data.strip() == "Hello, world!"
    cleanup_results()


def test_basic(loadLocalScenario):
    scenario = loadLocalScenario("basic.scenic")
    scenario.generate(maxIterations=1000)


@pickle_test
def test_pickle(loadLocalScenario):
    scenario = tryPickling(loadLocalScenario("basic.scenic"))
    tryPickling(sampleScene(scenario, maxIterations=1000))
