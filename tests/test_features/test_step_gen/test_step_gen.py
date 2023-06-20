import pytest
from refyre import Refyre
from refyre.fcluster import FileCluster
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

def test_step_gen():
    ref = Refyre(input_specs = ['specs/i.txt'])


    ref.create_spec('specs/o.txt', mode ="copy", track = True)
    assert not Path('a$').exists(), "Generator dir shouldn't be created"
    assert not Path('a0').exists(), "a0 hasn't been generated yet"

    for i in range(5):
        ref.step()
        assert Path(f"a{i}").exists(), f"Directory a{i} not created"
        assert Path(f"a{i}/a1.txt").exists(), f"a{i}/a1.txt doesn't exist"
        assert Path(f"a{i}/a2.txt").exists(), f"a{i}/a2.txt doesn't exist"
        assert len([*Path(f"a{i}").iterdir()]) == 2, f"{[*Path(f'a{i}').iterdir()]} has over 2 files"