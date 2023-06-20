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

def test_attribute_mispelling():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/incorrect_dir.txt'])

def test_missing_variable():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(output_specs = ['specs/incorrect_dir.txt'])

def test_missing_key():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/missing_key.txt'])
    
def test_missing_value():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/missing_value.txt'])
    
def test_missing_seperator():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/missing_seperator.txt'])

def test_multiline_comments():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/crazy_multiline.txt'])

def test_crazy_tabs_simple():

    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/crazy_tabs.txt'])

def test_normal_works():
    try:
        ref = Refyre(input_specs = ['specs/normal.txt'])
    except Exception as e:
        pytest.fail("This is the one normal spec")

def test_bad_clone_link_url():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/bad_clone.txt'])

def test_bad_clone_local_url():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/bad_clone_local.txt'])

def test_bad_clone_local_url():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/bad_clone_local.txt'])

def test_nonexistent_variable_output():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/normal2.txt'], output_specs = ['specs/output.txt'])

def test_out_of_bound_index():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/normal2.txt'], output_specs = ['specs/bad_slice.txt'])

def test_out_of_bound_slice():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/normal2.txt'], output_specs = ['specs/bad_slice2.txt'])

def test_bad_variable_name():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/normal2.txt'], output_specs = ['specs/bad_var_name.txt'])

def test_meticulous_single_line():
    try:
        ref = Refyre(input_specs = ['specs/meticulous_single_line.txt'])
    except Exception as e:
        pytest.fail("This just a meticulously commented spec, nothing syntactically wrong")

def test_commented_normal():
    try:
        ref = Refyre(input_specs = ['specs/commented_normal.txt'])
    except Exception as e:
        pytest.fail("This is a pretty nicely commented spec, no issue!")

def test_100th_test_case():
    assert True, "This is a free TC! LETS GOOOO BABY WE GOT A 100 OF THIS BANANASUCKERS TO WATCH OUT FOR!!!! :)"

def test_failed_generator():
    with pytest.raises(Exception) as e_info:
        ref = Refyre(input_specs = ['specs/failed_gen_input.txt'], output_specs = ['specs/failed_gen_output.txt'])
    
