import pytest
from refyre import Refyre
from refyre.fcluster import FileCluster
from pathlib import Path
import shutil

import re

import itertools


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

def test_zip():
    import zipfile
    print('imported zipfile')

    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    zipped = var1.zip()

    assert Path("out.zip").exists(), "Zip wasn't properly created"

    assert len(zipped) == 1

    print("ZIPPED", zipped)

    f = zipfile.ZipFile('out.zip')
    print(f.namelist())
    assert len(f.namelist()) == len(var1)

    zipped.delete()
    assert len(zipped) == 0

def test_contains():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    pth = [Path('in/1.txt'), Path('in/2.txt'), Path('in/3.txt'), Path('in/a.txt'), Path('in/b.txt'), Path('in/c.txt'), Path('in/f.txt')]

    for p in itertools.permutations(pth[:-2]):
        f = FileCluster(values = p)
        print(f)
        assert f in var1, f"{f} not in {var1}"
    
    
    assert FileCluster(values = [pth[-1]]) not in var1

def test_same_dir_copy():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    var1_copy = var1.copy("in")

    assert len(var1_copy) == len(var1)
    assert len(var1_copy + var1) == 2 * len(var1_copy)

    var1_copy.delete()

def test_diff_dir_copy():
    print("START COPY")
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    print('pre copy')
    var1_copy = var1.copy("out")
    print('post copy')

    assert len(var1_copy) == len(var1)
    assert len(var1_copy + var1) == 2 * len(var1_copy)

    var1_copy.delete()
    print("END COPY")

def test_diff_dir_move():

    print("DIFF DIR MOOOOVE\n\n\n")
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    print('move')
    var1_copy = var1.move("out")
    print('move 2')

    print(var1_copy, var1)
    assert len(var1_copy) != len(var1)
    assert len(var1_copy + var1) == len(var1_copy)

    print('move back')
    var1 = var1_copy.move("in")
    assert len(var1) == 6