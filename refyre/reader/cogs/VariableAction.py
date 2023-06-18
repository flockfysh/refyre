from .VariableParser import VariableParser
from refyre.fcluster import FileCluster
from refyre.config import log

import re

class VariableAction:
    '''
    External class that handles all of the variable updates,
    and provides an interface for the rest of the code to read & write 
    to variables

    Together, with the VariableParser, this class assembles "intent" that can 
    be used in specs.
    '''

    def __new__(self, expression, node, path, variable_dict, out_variable_dict , is_read, is_write, mode = ""):
        '''
        Reads in all parameters, and returns the name of the updated 
        variable

        Ironically, the is_read and is_write are defined in opposite.

        is_read refers to whether we are trying to read a value into the variable (which really just means "write"), but
        I'm keeping the naming this way since we're mostly doing the writing in specs focused on reading

        Similarly, is_write is for output specs
        '''

        #Currently, this operator pattern supports only + and "" (appending and defining)
        options_pattern = r'^(\+)?(.*)$' 

        match = re.match(options_pattern, node.name)
        operator = match.group(1) or ""
        name = match.group(2)

        #If the operator is "", a read command is sought
        '''
        Each of these commands have dual meanings - 

        "" in read means to read all the data to the variable
        "" in write means to 


        '''

        if is_read:
            if operator == "":
                out_variable_dict[name] = FileCluster.FileCluster(input_paths = [path], input_patterns = [node.pattern], recursive = "*r" in node.flags)

                if '*f' in node.flags:
                    out_variable_dict[name] = out_variable_dict[name].filter(lambda x : x.is_file())

                #*f flag - only keep directories
                if '*d' in node.flags:
                    out_variable_dict[name] = out_variable_dict[name].filter(lambda x : x.is_dir())

            elif operator == "+":
                
                p = FileCluster.FileCluster(input_paths = [path], input_patterns = [node.pattern], recursive = "*r" in node.flags)

                if '*f' in node.flags:
                    p = p.filter(lambda x : x.is_file())

                #*f flag - only keep directories
                if '*d' in node.flags:
                    p = p.filter(lambda x : x.is_dir())

                #Add a conditional in case they never defined a variable before
                out_variable_dict[name] = (p if name not in out_variable_dict else out_variable_dict[name] + p)


            return name, out_variable_dict[name] 
        
        if is_write:

            name, sliced, start, stop, step = VariableParser(name, variable_dict)

            #The refresher method will eliminate the invalid paths, so let's add back in the new paths at their original positions
            v = list(variable_dict[name].vals())

            if mode == "copy":
                log('copying ', name, 'to', path, sliced)
                sliced = sliced.copy(path)
                log('post copying ', name, 'to', path, sliced)
            
            elif mode == "cut":
                log('cut', name, 'to', path, sliced)
                sliced = sliced.move(path)
                log('post cut', name, 'to', path, sliced)
            


            if operator == '':
                s_v = sliced.vals()
                log(sliced, v, start, stop, step)
                for ind_s, ind_v in enumerate(range(start, stop, step)):
                    v[ind_v] = s_v[ind_s]
                log('updated vals', v)

                out_variable_dict[name] = variable_dict[name]
            elif operator == "+":
                log("APPENDING", variable_dict[name], v)


                out_variable_dict[name] += sliced

            return name, out_variable_dict[name]

        