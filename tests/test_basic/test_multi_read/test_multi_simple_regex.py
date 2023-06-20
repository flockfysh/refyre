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


def test_variable_read_sep_prelim():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    assert len(ref.get_vars()) == 1 and ref["var"] != None, "Variable isn't being properly detected"


def test_variable_read_sep_prelim():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    assert len(ref["var"]) == 6, f"{ref['var']} doesn't have 6 values."

def test_cluster_filter_numerical():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var1"]

    filtered = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

    for v in filtered:
        assert bool(re.search(r'\d', v.name)) == True, f"Path {v.name} doesn't contain a digit"
    
    assert len(filtered) == 3 and filtered == FileCluster(values = ['in/1.txt', 'in/2.txt', 'in/3.txt'], as_pathlib = False)

def test_cluster_filter_nonnumerical():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]

    filtered = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

    for v in filtered:
        assert not bool(re.search(r'\d', v.name)) == True, f"Path {v.name} DOES contain a digit"
    
    assert len(filtered) == 3 and filtered == FileCluster(values = ['in/a.txt', 'in/b.txt', 'in/c.txt'], as_pathlib = False)

def test_and_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var) == 6, "var should have 6 files"

    assert num_only & not_num == FileCluster(values = [])

def test_or_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var) == 6, "var should have 6 files"

    assert num_only | not_num == var, f"The union operator, {num_only | not_num} doesn't equal to {var}"


def test_plus_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var) == 6, "var should have 6 files"

    assert num_only + not_num == var, f"The addition operator, {num_only + not_num} doesn't equal to {var}"

def test_subtraction_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var) == 6, "var should have 6 files"

    assert var - num_only == not_num
    assert len(var) == 6, "filtering var shouldn't have modified var"
    assert len(num_only) == 3, "filtering num_only shouldn't have modified var"

    assert var - not_num  == num_only
    assert len(var) == 6, "filtering var shouldn't have modified var"
    assert len(not_num) == 3, "filtering not_num shouldn't have modified var"

    assert var - FileCluster(values = []) == var
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    assert var - var == FileCluster(values = [])
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

def test_dirs():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    dirs = var.dirs()

    assert len(dirs) == 1 and dirs.vals()[0] == Path('in')

def test_variable_num():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    assert len(ref.get_vars()) == 1, f"{len(ref.get_vars)} dict,  {ref.get_vars()} doesn't match expected"

def test_variable_dict():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    assert ref["var"] != None and type(ref["var"]) == FileCluster and len(ref["var"]) == 6

def test_cluster_filter_numerical():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]

    filtered = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

def test_cluster_filter_nonnumerical():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]

    filtered = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

def test_and_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert num_only & not_num == FileCluster(values = [])

def test_or_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"


    assert num_only | not_num == var, f"The union operator, {num_only | not_num} doesn't equal to {var}"


def test_plus_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert num_only + not_num == var, f"The addition operator, {num_only + not_num} doesn't equal to {var}"

def test_subtraction_cluster():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert len(var) == 6, "var should have 6 files"

    assert var - num_only == FileCluster(values = [])
    assert len(var) == 6, "filtering var shouldn't have modified var"

    assert var - not_num  == var
    assert len(var) == 6, "filtering var shouldn't have modified var"

    assert var - FileCluster(values = []) == var
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    assert var - var == FileCluster(values = [])
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

def test_dirs():
    ref = Refyre(input_specs = ["specs/input_reg.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    dirs = var.dirs()

    assert len(dirs) == 3 and dirs.vals()[0] == Path('a1')
