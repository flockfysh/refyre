import pytest
from refyre import Refyre
from refyre.config import logger
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


def test_multi_var():
    assert Path('in').exists(), "Input directory doesn't exist - weird"
    ref = Refyre(input_specs = ['specs/in.txt'], output_specs = ['specs/out.txt'])

    
    assert Path('out').exists(), "Output directory not created"
    assert Path('out/a/a.txt').exists(), "a.txt doesn't exist"
    assert Path('out/both/a.txt').exists(), "a.txt doesn't exist"
    assert Path('out/both/b.txt').exists(), "a.txt doesn't exist"
