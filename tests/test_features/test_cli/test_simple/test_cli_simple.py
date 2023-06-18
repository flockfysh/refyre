import pytest
from refyre import Refyre, main
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

#ref: https://jugmac00.github.io/blog/testing-argparse-applications-the-better-way/
def test_main_even_simpler(capsys):
    main(["-i", "specs/input.txt", "-o", "specs/output2.txt"])
    assert Path('c1').exists() and Path('c2').exists() and len([*Path('c1').iterdir()]) == 1 and len([*Path('c2').iterdir()]) == 3

def test_gen_var_check(capsys):
    main(["-i", "specs/input.txt", "-o", "specs/output.txt"]) 
    assert len([*Path('c').iterdir()]) == 4