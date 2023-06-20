import pytest
from refyre import Refyre
from refyre.cluster import FileCluster
from pathlib import Path
import re
import sys
import shutil

#Setup and tear down each test
@pytest.fixture(autouse=True)
def run_before_and_after_tests(monkeypatch):
    """Fixture to execute asserts before and after a test is run"""
    
    # Setup: 
    shutil.copytree('assets', 'test')
    cwd = Path.cwd()
    monkeypatch.chdir('test')
    p = list(sys.path)

    yield # this is where the testing happens

    # Teardown : fill with any logic you want
    monkeypatch.chdir(str(cwd))
    shutil.rmtree('test')
    FileCluster.wipe()
    sys.path = p


def test_code_import_file():
    ref = Refyre(input_specs = ['specs/code_simple.txt'])
    
    from dummymath.module1.add import silly_add, silly_zero

    assert silly_add(1, 1) == 0, "Wrong silly add function imported"
    assert silly_zero(1, 1) == 1, "Wrong silly zero function imported"

def test_code_import_multiple_files():
    ref = Refyre(input_specs = ['specs/code_simple.txt'])
    
    from dummymath.module1.add import silly_add, silly_zero

    assert silly_add(1, 1) == 0, "Wrong silly add function imported"
    assert silly_zero(1, 1) == 1, "Wrong silly zero function imported"

    from dummymath.module2.mut import mutt

    assert mutt() == 1, "Wrong mutt() function imported"

def test_code_import_submodule():
    ref = Refyre(input_specs = ['specs/code_module.txt'])
    

    from module1.add import silly_add, silly_zero

    assert silly_add(1, 1) == 0, "Wrong silly add function imported"
    assert silly_zero(1, 1) == 1, "Wrong silly zero function imported"


def test_code_import_nested_submodule():
    ref = Refyre(input_specs = ['specs/code_module.txt'])
    

    from module1.add import silly_add, silly_zero

    assert silly_add(1, 1) == 0, "Wrong silly add function imported"
    assert silly_zero(1, 1) == 1, "Wrong silly zero function imported"

def test_code_import_nested_submodule():
    ref = Refyre(input_specs = ['specs/code_submodule.txt'])
    
    print(ref.code_manager.module_dirs)

    from m1.add import silly_add, silly_zero

    assert silly_add(1, 1) == 0, "Wrong silly add function imported"
    assert silly_zero(1, 1) == 1, "Wrong silly zero function imported"
