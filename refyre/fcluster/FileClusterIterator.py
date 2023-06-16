
class FileClusterIterator:
    '''
        A simple iterator to run through the variable data
    '''
    def __init__(self, variable):
        self.var_vals = variable.vals()
        self.index = -1

    def __next__(self):

        if self.index + 1 >= len(self.var_vals):
            raise StopIteration
        
        self.index += 1
        r = self.var_vals[self.index]
        return r