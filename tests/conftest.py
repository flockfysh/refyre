import sys
from pathlib import Path
import pytest
import shutil 

sys.path.insert(0, Path('').absolute().as_posix())

import refyre

#Note: make sure to run tests from the base directory (/refyre-base)


#Automatically change directory to test dir
@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)


#Remove all pycache folders
def pytest_sessionstart(session):
    root_path = Path.cwd()
    pycache_folders = root_path.glob("**/__pycache__")

    for pycache_folder in pycache_folders:
        if pycache_folder.is_dir():
            shutil.rmtree(pycache_folder)