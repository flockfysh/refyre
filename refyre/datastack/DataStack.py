from refyre.utils import optional_dependencies 

with optional_dependencies("warn"):
    import numpy as np 
    import pandas as pd
    import matplotlib.pyplot as plt

# The PandasStack class is a Python class that creates a Pandas dataframe from a list of variables
# using a mapper function.
class PandasStack:

    def __init__(self, association):
        self.association = association 
    
    def create_dataframe(self, col_names, mapper_func):
        '''
            col_names: List[String] An array of the names of the columns of the dataframe
            mapper_func: A function that takes in input of a tuple (var1_output, var2_output, ...), and returns a tuple with values for each of the columns
                - Note each tuple value should be the value for the corresponding columns (i.e the ith col_name should be associated with the ith tuple val)
        '''

        out_dct = {}

        for n in col_names:
            out_dct[n] = []

        for input_tuple in self.association:

            output_data = mapper_func(*input_tuple)
            assert len(output_data) == len(col_names), "The data length and number of columns specified through the column names don't match up!"

            for i in range(len(col_names)):
                out_dct[col_names[i]].append(output_data[i])

        return pd.DataFrame.from_dict(out_dct)

class NumpyStack:

    def __init__(self, variables_array):
        self.variables_array = variables_array
    
    def create_numpy(self, processing_function):
        '''
            processing_function: 
        '''
        pass 




