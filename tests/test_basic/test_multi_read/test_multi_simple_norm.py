import pytest
from refyre import Refyre
from refyre.cluster import FileCluster
from pathlib import Path
import re
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

def test_prelim():
    ref = Refyre(input_specs = ["specs/input.txt"])
    assert len(ref.get_vars()) == 1 and ref["var"] != None, "Variable isn't being properly detected"


def test_variable_read_sep_prelim_len():
    ref = Refyre(input_specs = ["specs/input.txt"])
    assert len(ref["var"]) == 2, f"{ref['var']} doesn't have 2 values."
