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

'''
Things to test

clone:
    - Basic clone
    - YOLOv5 test clone

clone & filter out files
    - YOLOv5 filter

clone & code import
    - YOLOv5 code import
    - other repository code import

'''

def test_clone_yolo():
    ref = Refyre(input_specs = ["specs/clone_basic.txt"])
    var = ref["var"]

    assert FileCluster(values = ["clone_folder/data", "clone_folder/segment"]) in var, f"Couldn't find folder in {var}" 

def test_clone_yolo_and_filter():
    ref = Refyre()
    ref.create_spec('specs/clone_filter.txt')

    assert len([*Path('clone_folder').iterdir()]) == 2, f"{[*Path('clone_folder').iterdir()]} doesn't only have 2 files"

def test_clone_yolo_and_filter_reg():
    ref = Refyre()
    ref.create_spec('specs/clone_filter_reg.txt')

    assert len([*Path('clone_folder').iterdir()]) == 2, f"{[*Path('clone_folder').iterdir()]} doesn't only have 2 files"

def test_clone_yolo_and_filter_reg_dirs_only():
    ref = Refyre()
    ref.create_spec('specs/clone_dirs_only.txt')

    assert len([*Path('clone_folder').iterdir()]) == 7, f"{[*Path('clone_folder').iterdir()]} doesn't only have 7 directories"
    assert len([*Path('clone_folder/data').iterdir()]) > 0, "Shouldn't delete files from subdirectories"


