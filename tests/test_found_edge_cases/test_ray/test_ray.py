import pytest
from refyre import Refyre, main
from refyre.cluster import FileCluster
from pathlib import Path
from refyre.config import logger
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

def test_ray_main(capsys):
    assert Path('ray').exists(), "Test is setup incorrectly"
    assert (Path('ray') / 'in-0').exists(), "in dir from tests is setup incorrectly"

    main(["-i", "specs/in.txt", "-o", "specs/out.txt"])

    logger.debug([*Path('ray').iterdir()])
    assert (Path('ray') / 'in-0').exists() and len([*(Path('ray') / 'in-0').iterdir()]) == 0, "the input directory somehow got messed up"
    assert (Path('ray') / 'out-0').exists(), "the output directory wasn't created"
    assert (Path('ray') / 'out-0' / 'test').exists(), "the test directory wasn't created"
