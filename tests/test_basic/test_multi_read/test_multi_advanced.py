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

limit:
    - read
    - generate

'''

def test_read_limit():
    ref = Refyre(input_specs = ["specs/input_limit.txt"])
    var = ref["var"]

    assert len(var) == 4 and FileCluster(values = ["a1/a11.txt", "a1/a12.txt", "a2/a21.txt", "a2/a22.txt"]) in var, f"Desired values not in {var}"

def test_generate_limit():
    ref = Refyre(input_specs = ["specs/input_limit.txt"])
    var = ref["var"]

    assert len(var) == 4 and FileCluster(values = ["a1/a11.txt", "a1/a12.txt", "a2/a21.txt", "a2/a22.txt"]) in var, f"Desired values not in {var}"

    ref.create_spec('specs/output_limit.txt')

    for i in range(4, 6):
        assert len([*Path(f"a{i}").iterdir()]) == 4, f"Files not copied properly, directory a{i} has files {[*Path(f'a{i}').iterdir()]}"

def test_extreme_conflict_prelim():
    ref = Refyre(input_specs = ["specs/input_glob.txt"])
    var = ref["var"]

    a1 = var.filter(lambda p : 'a1' in p.name)
    a2 = var.filter(lambda p : 'a2' in p.name)
    a3 = var.filter(lambda p : 'a3' in p.name)


    #Starts at i = 0
    a1 = a1.rename(lambda i : f'f{i + 1}.txt')
    a2 = a2.rename(lambda i : f'f{i + 1}.txt')
    a3 = a3.rename(lambda i : f'f{i + 1}.txt')


    a1 = a1.move('a3')
    a2 = a2.move('a3')

    assert var == FileCluster(values = ["a3/f1.txt", "a3/f2.txt", "a3/f1(1).txt", "a3/f2(1).txt", "a3/f1(2).txt", "a3/f2(2).txt"]), f"Var {var} doesn't match desired."

def test_copy_duplicate():
    ref = Refyre(input_specs = ["specs/input_glob.txt"])
    var = ref["var"]
    var_cloned = var.clone()

    a1 = var.filter(lambda p : 'a1' in p.name)
    a2 = var.filter(lambda p : 'a2' in p.name)
    a3 = var.filter(lambda p : 'a3' in p.name)

    a1_copy = a1.copy('a1')
    a2_copy = a2.copy('a2')
    a3_copy = a3.copy('a3')

    assert len(a1_copy) == len(a1), "Copy didn't copy all the files"
    assert len(a2_copy) == len(a2), "Copy didn't copy all the files"
    assert len(a3_copy) == len(a3), "Copy didn't copy all the files"

    assert len([*Path('a1').iterdir()]) == 2 * len(a1)
    assert len([*Path('a2').iterdir()]) == 2 * len(a2)
    assert len([*Path('a3').iterdir()]) == 2 * len(a3)

    assert var == var_cloned, "Values were somehow modified"

def test_zip_copy_duplicate():
    ref = Refyre(input_specs = ["specs/input_glob.txt"])
    var = ref["var"]
    var_cloned = var.clone()

    a1 = var.filter(lambda p : 'a1' in p.name)
    a2 = var.filter(lambda p : 'a2' in p.name)
    a3 = var.filter(lambda p : 'a3' in p.name)

    a1_zipped = a1.zip('a1')
    a2_zipped = a2.zip('a2')
    a3_zipped = a3.zip('a3')

    assert len([*Path('a1').iterdir()]) == 3, f"Zip not properly added to a1, {[*Path('a1').iterdir()]}"
    assert len([*Path('a2').iterdir()]) == 3, "Zip not properly added to a2"
    assert len([*Path('a3').iterdir()]) == 3, "Zip not properly added to a3"

    a1_copy = a1.copy('a1')
    a2_copy = a2.copy('a2')
    a3_copy = a3.copy('a3')

    assert len([*Path('a1').iterdir()]) == 5, "Copy not properly happening in a1"
    assert len([*Path('a2').iterdir()]) == 5, "Copy not properly happening in a2"
    assert len([*Path('a3').iterdir()]) == 5, "Copy not properly happening in a3"

    a1_zipped_2 = a1_copy.zip('a1')
    a2_zipped_2 = a2_copy.zip('a2')
    a3_zipped_2 = a3_copy.zip('a3')

    assert len([*Path('a1').iterdir()]) == 6, "Zip not properly added to a1"
    assert len([*Path('a2').iterdir()]) == 6, "Zip not properly added to a2"
    assert len([*Path('a3').iterdir()]) == 6, "Zip not properly added to a3"