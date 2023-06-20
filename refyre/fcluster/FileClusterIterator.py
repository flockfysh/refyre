
class FileClusterIterator:
    '''
        A simple iterator to run through the variable data
    '''
    def __init__(self, variable):
        self.var_vals = variable.vals()
        self.index = -1

    def __next__(self):
        """
        This is an implementation of the `__next__` method for an iterator that raises a `StopIteration`
        exception when the end of the iterator is reached.
        :return: The `__next__` method is returning the next value in the `var_vals` list after
        incrementing the `index` by 1.
        """

        if self.index + 1 >= len(self.var_vals):
            raise StopIteration
        
        self.index += 1
        r = self.var_vals[self.index]
        return r