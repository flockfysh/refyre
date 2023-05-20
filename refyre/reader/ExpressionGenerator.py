import re 

def create_lambda_generator_function(expression):
    # Replace '$' with '{}' to use it as a placeholder for string formatting
    lambda_function = lambda i: expression.replace('$', str(i))

    return lambda_function

def extract_key_elements(string):
    pattern = r'^(\w+)(?:\[(\d+)?:(\d+)?:(\d+)?\])?$'
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
    '''

    start, stop, step = 0 if start is None else start, len(var) if stop is None else stop, 1 if step is None else step
    return slice(start, stop, step)



