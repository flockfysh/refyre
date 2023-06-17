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
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    assert len(ref.get_vars()) == 1 and ref["var"] != None, "Variable isn't being properly detected"


def test_variable_read_sep_prelim():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    assert len(ref["var"]) == 6, f"{ref['var']} doesn't have 6 values."


def test_cluster_filter_numerical():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var1"]

    filtered = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

    for v in filtered:
        assert bool(re.search(r'\d', v.name)) == True, f"Path {v.name} doesn't contain a digit"
    
    assert len(filtered) == 3 and filtered == FileCluster(values = ['in/1.txt', 'in/2.txt', 'in/3.txt'], as_pathlib = False)

def test_cluster_filter_nonnumerical():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    filtered = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

    for v in filtered:
        assert not bool(re.search(r'\d', v.name)) == True, f"Path {v.name} DOES contain a digit"
    
    assert len(filtered) == 3 and filtered == FileCluster(values = ['in/a.txt', 'in/b.txt', 'in/c.txt'], as_pathlib = False)

def test_and_cluster():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
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
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
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
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
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
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
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
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    dirs = var.dirs()

    assert len(dirs) == 1 and dirs.vals()[0] == Path('in')

def test_variable_num():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    assert len(ref.get_vars()) == 1, f"{len(ref.get_vars)} dict,  {ref.get_vars()} doesn't match expected"

def test_variable_dict():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    assert ref["var"] != None and type(ref["var"]) == FileCluster and len(ref["var"]) == 6

def test_cluster_filter_numerical():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    filtered = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

def test_cluster_filter_nonnumerical():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    filtered = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering filtered shouldn't have modified var"

def test_and_cluster():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert num_only & not_num == FileCluster(values = [])

def test_or_cluster():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"


    assert num_only | not_num == var, f"The union operator, {num_only | not_num} doesn't equal to {var}"


def test_plus_cluster():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    num_only = var.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering num_only shouldn't have modified var"

    not_num = var.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var) == 6, "filtering not_num shouldn't have modified var"

    assert num_only + not_num == var, f"The addition operator, {num_only + not_num} doesn't equal to {var}"

def test_subtraction_cluster():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
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
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]
    assert len(var) == 6, "var should have 6 files"

    dirs = var.dirs()

    assert len(dirs) == 3 and dirs.vals()[0] == Path('a1')

def test_move_to_existing_folder():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    var_moved = var.move("a1")

    assert len(var) == 2, f"Old files weren't properly moved {var}"

    assert len(var_moved) == 6, f'Some files were accidentally deleted {var_moved}'
    assert len([*Path("a1").iterdir()]) == 6, "There aren't 6 files in a1"

    var = var_moved.clone()
    assert var == var_moved, "Clones should be equal in content"
    assert var is not var_moved, "Object references are the same when we sought to clone object"

    print("PRE PRINT VAR", var)
    var_moved = var.move("a2")
    assert len(var_moved) == 6, f'Some files were accidentally deleted {var_moved}'

    print("PRINT VAR", var)
    assert var == FileCluster(values = []), f"Old files weren't properly moved {var}"

    assert len(var_moved) == 6, f'Some files were accidentally deleted {var_moved}'
    assert len([*Path("a2").iterdir()]) == 6, "There aren't 6 files in a2"

    var = var_moved.clone()

    assert var == var_moved, "Clones should be equal in content"
    assert var is not var_moved, "Object references are the same when we sought to clone object"

    var_moved = var.move("a3")
    assert len(var_moved) == 6, f'Some files were accidentally deleted {var_moved}'
    assert var == FileCluster(values = []), f"Old files weren't properly moved {var}"

    assert len(var_moved) == 6, f'Some files were accidentally deleted {var_moved}'
    assert len([*Path("a3").iterdir()]) == 6, "There aren't 6 files in a3"

def test_serialize():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    var_renamed = var.rename(lambda i : f"file{i}.txt")

    for i, f in enumerate(var_renamed):
        assert f.name == f"file{i}.txt", f"File {f.name} not properly named"

def test_filter_and_delete():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    filtered_var = var.filter(lambda p : "a1" in p.name)

    assert filtered_var in var, f"{filtered_var} not in {var} even though it should"
    assert len(filtered_var) == 2, "Length of filtered variable should be 2"

    filtered_var.delete()

    assert len(var) == 4,  "Variable changes weren't broadcasted"

def test_filter_and_move():
    ref = Refyre(input_specs = ["specs/input_gen.txt"])
    var = ref["var"]

    a1 = var.filter(lambda p : "a1" in p.name)
    a2 = var.filter(lambda p : "a2" in p.name)
    a3 = var.filter(lambda p : "a3" in p.name)

    assert a1 + a2 + a3 == var, f"Sum of each folder files should equal total"

    a1 = a1.move("a2")

    assert len([*Path('a2').iterdir()]) == 4, "Length doesn't properly match up"

    a2 += a1

    a21 = a2.filter(lambda p : "a1" in p.name)

    a2 -= a21 

    a21 = a21.move('a1')

    assert a21 + a2 + a3 == var