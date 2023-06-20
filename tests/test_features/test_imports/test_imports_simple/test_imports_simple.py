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

def test_imports():
    ref = Refyre(input_specs = ['specs/input.txt'])

    assert 'bvar' in ref, "bvar not found in ref"
    assert ref['bvar'] == FileCluster(values = ['in/b/b1.txt', 'in/b/b2.txt']), f"{ref['bvar']} doesn't match expected"

