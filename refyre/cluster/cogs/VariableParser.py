import re 
from refyre.cluster import FileCluster
from refyre.config import logger

class VariableParser:
    '''
    A static class parser designed specifically to identify and evaluate expressions
    relating to variables. This class is the most relevant to the
    node.name attribute, and will normally be used to parse it.
    '''
    def extract_variable_data(expression):
        pattern1 = r'^([\w-]+)(?:\[(\d+)?:(\d+)?(?:\:(\d+))?\])?$'
        pattern2 = r'^([\w-]+)\[(\d+)\]$'

        match1 = re.match(pattern1, expression)
        match2 = re.match(pattern2, expression)

        logger.debug(f'{match1}, {match2}')

        if match1:
            logger.debug('match1')
            name = match1.group(1)
            start = match1.group(2)
            stop = match1.group(3)
            step = match1.group(4)

            return name, start, stop, step

        elif match2:
            logger.debug('match2')
            name = match2.group(1)
            start = match2.group(2)
            stop = str(int(start) + 1)
            step = None

            return name, start, stop, step

        else:
            return None

    def get_slice(var, start, stop, step):
        '''
        Input:
            - Var: the FileCluster variable we seek to obtain a slice from
            - Start: the start of the slice, 0 if nothing specified
            - Stop: the stop of the slice, length if nothing specified
            - Step: the step of the slice, 1 if nothing specified 
        
        Returns a slice object involving the three indices
        '''
        assert type(var) == FileCluster

        start, stop, step = 0 if start is None else int(start), len(var) if stop is None else int(stop), 1 if step is None else int(step)
        return slice(start, stop, step), start, stop, step
    
    def __new__(self, expression, variable_dict):
        '''
            Hijack the '__new__' method (usually used in constructors) 
            and make it do our bidding >:)

            Takes in an expression, and returns the name of the variable, and the sequence of variable requested.
        '''

        out_data = VariableParser.extract_variable_data(expression)

        if not out_data:
            raise Exception(f"Expression {out_data} isn't a valid expression.")

        name, start, stop, step = out_data

        if name not in variable_dict:
            raise Exception(f"{name} is not a recognized variable in variable dict {variable_dict}")

        desired_slice, start, stop, step = VariableParser.get_slice(variable_dict[name], start, stop, step)
        variable_slice = variable_dict[name][desired_slice]

        #Return the variable name, and the subset requested
        return name, variable_slice, start, stop, step