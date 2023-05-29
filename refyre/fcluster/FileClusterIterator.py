
class FileClusterIterator:
    '''
        A simple iterator to run through the variable data
    '''
    def __init__(self, variable):
        self.var = variable
        self.index = -1

    def __next__(self):

        if self.index + 1 >= len(self.var):
            raise StopIteration
        
        self.index += 1
        r = self.var[self.index].vals()[0]
        return r