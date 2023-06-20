import pytest
from refyre import Refyre
from refyre.cluster import FileCluster
from pathlib import Path
import re
import requests
import shutil

#Setup and tear down each test
@pytest.fixture(autouse=True)
def run_before_and_after_tests(monkeypatch):
    """Fixture to execute asserts before and after a test is run"""
    
    # Setup: 
    shutil.copytree('assets', 'test')
    cwd = Path.cwd()
    monkeypatch.chdir('test')

    yield # this is where the testing happens

    # Teardown : fill with any logic you want
    monkeypatch.chdir(str(cwd))
    shutil.rmtree('test')
    FileCluster.wipe()

def test_imports_exp():
    ref = Refyre(input_specs = ['specs/input.txt'])
    ref.create_spec('specs/gen.txt', track = True)

    assert len([*Path('exps').iterdir()]) == 0, "No experiments have been created yet"

    for i in range(1, 6):
        ref.step()
        assert len([*Path('exps').iterdir()]) == i, "No experiments have been created yet"
