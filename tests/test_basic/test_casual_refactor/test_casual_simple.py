import pytest
from refyre import Refyre
from refyre.fcluster import FileCluster
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


def test_variable_read_sep_prelim():
    ref = Refyre(input_specs = ["input_sep.txt"])
    assert len(ref.get_vars()) == 2, f"{len(ref.get_vars)} dict,  {ref.get_vars()} doesn't match expected"

def test_variable_read_sep_a():
    ref = Refyre(input_specs = ["input_sep.txt"])
    avar = ref["var1"]
    
    assert len(avar) == 2 and avar[0].item() == Path('a/a1.txt') and avar[1].item() == Path('a/a2.txt')

def test_variable_read_sep_b():
    ref = Refyre(input_specs = ["input_sep.txt"])
    avar = ref["var2"]
    
    assert len(avar) == 2 and avar[0].item() == Path('b/b1.txt') and avar[1].item() == Path('b/b2.txt')

def test_gen_var_check():
    ref = Refyre(input_specs = ["input.txt"], output_specs = ['output.txt'])
    v = ref["var"]
    
    assert len(v) == 4  and len([*Path('c').iterdir()]) == 4

def test_gen_var_easy2():
    ref = Refyre(input_specs = ["input.txt"])
    ref.create_spec("output2.txt")
    
    assert Path('c1').exists() and Path('c2').exists() and len([*Path('c1').iterdir()]) == 1 and len([*Path('c2').iterdir()]) == 3