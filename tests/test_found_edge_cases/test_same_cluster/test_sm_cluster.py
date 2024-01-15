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

def test_same_cluster_main(capsys):

    main(["-i", "specs/in.txt", "-o", "specs/out.txt"])

    logger.debug([*Path('out').rglob('**/*')])
    assert Path('out').exists(), "out directory doesn't exist"
    assert Path('out/ab/a.txt').exists(), "files directory doesn't exist"
    assert Path('out/ab/b.txt').exists(), "files directory doesn't exist"
    assert Path('out/bc/b.txt').exists(), "files directory doesn't exist"
    assert Path('out/bc/c.txt').exists(), "files directory doesn't exist"
    assert len([*Path('out/bc').iterdir()]) == 2
    assert len([*Path('out/ab').iterdir()]) == 2
