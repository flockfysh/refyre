import pytest
from refyre import Refyre
from refyre.fcluster import FileCluster
from pathlib import Path
from unittest.mock import patch
import re
import requests
import shutil


from refyre.datastack import PandasStack
from PIL import Image
import pandas as pd


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

def test_pandas_stack_simple():
    ref = Refyre(input_specs = ['specs/in.txt'])

    #We will do some pandas visualizations on the input data
    stack = PandasStack([ref["images"]])

    def processor(tup):
        fp = tup[0]
        print('processing', fp)
        im = Image.open(fp).convert('RGB')
        width, height = im.size 

        ar, ag, ab = 0.0, 0.0, 0.0
        for i in range(width):
            for j in range(height):
                r, g, b = im.getpixel((i, j))
                ar, ag, ab = ar + r, ag + g, ab + b 
            
        ar, ag, ab = ar / (width * height), ag / (width * height), ab / (width * height)
        return (fp.name, width, height, ar, ag, ab)

    df = stack.create_dataframe(['image_name', 'image_width', 'image_height', 'average_red', 'average_green', 'average_blue'], processor)

    assert 'image_name' in df.columns and 'average_blue' in df.columns, f"Dataframe {df} not properly created" 
    assert len(df.index) == 2, f"{len(df.index)} not equal 2 and not accurate"
 