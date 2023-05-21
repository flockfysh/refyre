import re 

class VariableParser:
    '''
    A static class parser designed specifically to identify and evaluate expressions
    relating to variables. This class is the most relevant to the
    node.name attribute, and will normally be used to parse it.
    '''
    def extract_variable_data(string):
        '''
        Extracts the key components of a variable expression.

        We define the key information to be the variable name and the start, stop, and step indices.

        Such an expression could look like

        var1 --> return the entire var
        var1[0] --> return only the first value
        var1[0:5]--> return the first values 
        var1[0:10:2] --> return values between 0-10, skipping by 2
        '''
        pattern = r'^(\w+)(?:\[(\d+)?:(\d+)?(?:\:(\d+))?\])?$'
        match = re.match(pattern, string)

        if match:
            name = match.group(1)
            start_index = match.group(2)
            stop_index = match.group(3)
            step_index = match.group(4)

            # Convert start_index, stop_index, and step_index to integers if they exist
            start_index = int(start_index) if start_index is not None else None
            stop_index = int(stop_index) if stop_index is not None else None
            step_index = int(step_index) if step_index is not None else None

            return name, start_index, stop_index, step_index
        else:
            return None, None, None, None

    def get_slice(var, start, stop, step):
        '''
        Input:
            - Var: the FileCluster variable we seek to obtain a slice from
            - Start: the start of the slice, 0 if nothing specified
            - Stop: the stop of the slice, length if nothing specified
            - Step: the step of the slice, 1 if nothing specified 
        
        Returns a slice object involving the three indices
        '''

        start, stop, step = 0 if start is None else start, len(var) if stop is None else stop, 1 if step is None else step
        return slice(start, stop, step)