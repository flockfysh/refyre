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

def test_simple_alias():
    ref = Refyre(input_specs = ['specs/alias_seperate.txt'])
    
    aliases = ref.aliases()

    assert aliases['adir'] == Path('a1') and aliases['bdir'] == Path('a2')

def test_generator_alias():
    ref = Refyre(input_specs = ['specs/alias_gen.txt'])
    
    aliases = ref.aliases()

    assert aliases['dir1'] == Path('a1') and aliases['dir2'] == Path('a2')