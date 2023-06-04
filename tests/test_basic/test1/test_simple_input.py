import pytest
from refyre import Refyre
from refyre.fcluster import FileCluster
from pathlib import Path
import re

@pytest.fixture(autouse=True)
def change_test_dir(request, monkeypatch):
    monkeypatch.chdir(request.fspath.dirname)

def test_variable_num():
    ref = Refyre(input_specs = ["input.txt"])
    assert len(ref.get_vars()) == 1, f"{len(ref.get_vars)} dict,  {ref.get_vars()} doesn't match expected"

def test_variable_dict():
    ref = Refyre(input_specs = ["input.txt"])
    assert ref["var1"] != None and type(ref["var1"]) == FileCluster and len(ref["var1"]) == 6

def test_cluster_filter_numerical():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    filtered = var1.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering filtered shouldn't have modified var1"

    for v in filtered:
        assert bool(re.search(r'\d', v.name)) == True, f"Path {v.name} doesn't contain a digit"
    
    assert len(filtered) == 3 and filtered == FileCluster(values = ['in/1.txt', 'in/2.txt', 'in/3.txt'], as_pathlib = False)

def test_cluster_filter_nonnumerical():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]

    filtered = var1.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering filtered shouldn't have modified var1"

    for v in filtered:
        assert not bool(re.search(r'\d', v.name)) == True, f"Path {v.name} DOES contain a digit"
    
    assert len(filtered) == 3 and filtered == FileCluster(values = ['in/a.txt', 'in/b.txt', 'in/c.txt'], as_pathlib = False)

def test_and_cluster():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    num_only = var1.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering num_only shouldn't have modified var1"

    not_num = var1.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering not_num shouldn't have modified var1"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var1) == 6, "var1 should have 6 files"

    assert num_only & not_num == FileCluster(values = [])

def test_or_cluster():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    num_only = var1.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering num_only shouldn't have modified var1"

    not_num = var1.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering not_num shouldn't have modified var1"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var1) == 6, "var1 should have 6 files"

    assert num_only | not_num == var1, f"The union operator, {num_only | not_num} doesn't equal to {var1}"


def test_plus_cluster():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    num_only = var1.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering num_only shouldn't have modified var1"

    not_num = var1.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering not_num shouldn't have modified var1"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var1) == 6, "var1 should have 6 files"

    assert num_only + not_num == var1, f"The addition operator, {num_only + not_num} doesn't equal to {var1}"

def test_subtraction_cluster():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    num_only = var1.filter(lambda x : any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering num_only shouldn't have modified var1"

    not_num = var1.filter(lambda x : not any(i.isdigit() for i in x.name))
    assert len(var1) == 6, "filtering not_num shouldn't have modified var1"

    assert len(num_only) == 3, "Num only should have 3 files"
    assert len(not_num) == 3, "Not num should have 3 files"
    assert len(var1) == 6, "var1 should have 6 files"

    assert var1 - num_only == not_num
    assert len(var1) == 6, "filtering var1 shouldn't have modified var1"
    assert len(num_only) == 3, "filtering num_only shouldn't have modified var1"

    assert var1 - not_num  == num_only
    assert len(var1) == 6, "filtering var1 shouldn't have modified var1"
    assert len(not_num) == 3, "filtering not_num shouldn't have modified var1"

    assert var1 - FileCluster(values = []) == var1
    assert len(var1) == 6, "filtering num_only shouldn't have modified var1"

    assert var1 - var1 == FileCluster(values = [])
    assert len(var1) == 6, "filtering num_only shouldn't have modified var1"


def test_dirs():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    dirs = var1.dirs()

    assert len(dirs) == 1 and dirs.vals()[0] == Path('in')

def test_filecluster_obj_copy_simple():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    var1_copy = var1.clone()

    assert var1 == var1_copy, "Equality check failed"
    assert var1 is not var1_copy, "Identity / reference check failed - objects shouldn't have same reference"

def test_obj_copy_equality():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    var1_copy = var1.clone()
    var1_copy_copy = var1_copy.clone()

    for a, b, c in zip(var1, var1_copy, var1_copy_copy):
        assert a == b and b == c
    
def test_obj_move_same_directory():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    moved = var1.move("in")

    assert moved == var1, f"Moving to the same directory shouldn't alter the contents of the FileCluster, but premoved {var1} -> {moved}"

def test_refyre_save():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    ref.save()

    assert Path("refyre_state.json").exists(), "Save file wasn't properly generated"

    var2 = FileCluster(values = ["refyre_state.json"])

    ref2 = Refyre.load("refyre_state.json")

    assert ref2["var1"] != None and type(ref2["var1"]) == FileCluster and len(ref2["var1"]) == 6

    assert ref["var1"] == ref2["var1"], "Saving shouldn't alter the state of the variables"

    assert len(var2) == 1
    var2.delete()
    assert len(var2) == 0

def test_slices():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    assert var1[0].item() == Path("in/1.txt")
    assert var1[1].item() == Path("in/2.txt")
    assert var1[2].item() == Path("in/3.txt")
    assert var1[3].item() == Path("in/a.txt")
    assert var1[4].item() == Path("in/b.txt")
    assert var1[5].item() == Path("in/c.txt")

def test_slices_intermediate():
    ref = Refyre(input_specs = ["input.txt"])
    var1 = ref["var1"]
    assert len(var1) == 6, "var1 should have 6 files"

    assert var1[0:2].vals() == [Path("in/1.txt"), Path("in/2.txt")], "Normal slice isn't working"
    assert len(var1) == 6, "var1 should have 6 files"

    assert var1[0::-1].vals() == [Path("in/1.txt"), ], f"Reverse slice {var1[0:2:-1].vals()} isn't working "
