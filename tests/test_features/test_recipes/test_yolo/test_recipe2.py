import pytest
from refyre import Refyre 
from refyre.cluster import FileCluster
from refyre.core import RecipePreprocessor

from pathlib import Path
import re
import requests
import shutil
import sys

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


def test_recipe():
    ref = RecipePreprocessor('specs/install.yaml')

    assert Path('dev_env').exists(), "Dev env wasn't created"
    assert (Path('dev_env') / 'bin' / 'python').exists(), "Path to python does exist"