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

def test_nest_prelim():
    ref = Refyre(input_specs = ['specs/in.txt'])
    assert len(ref) == 1,  f"{len(ref)} doesn't match intended len."

    nests = ref["nests"]
    assert len(nests) == 2, f"{nests} Only two files should be targeted"

def test_nest_decompress():
    ref = Refyre(input_specs = ['specs/in.txt'])
    assert len(ref) == 1,  f"{len(ref)} doesn't match intended len."

    nests = ref["nests"]
    decomp = nests.decompress()

    assert len(decomp) == 4, f"{decomp} Only two files should be targeted"

def test_nest_decompress_rec():
    ref = Refyre(input_specs = ['specs/in.txt'])
    assert len(ref) == 1,  f"{len(ref)} doesn't match intended len."

    nests = ref["nests"]
    decomp = nests.decompress(complete = True)

    assert len(decomp) == nests.filecount(), f"{decomp} num files doesn't equal recursive total"

def test_nest_prelim_diff():
    ref = Refyre(input_specs = ['specs/in_diff.txt'])
    assert len(ref) == 1,  f"{len(ref)} doesn't match intended len."

    nests = ref["nests"]
    assert len(nests) == 4, f"{nests} Only two files should be targeted"