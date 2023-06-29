from pathlib import Path  
from refyre.config import logger
from joblib import Parallel

class Parallelizer:
    def __init__(self, *args, **kwargs):
        if 'use' in kwargs and kwargs['use']:
            self.parallelize = kwargs['use'] 
        else:
            self.parallelize = True

    def __call__(self, func):
        '''
        Parallelize the given method.

        1. Find the optimal number of threads
        2. Parallelize the method to handle those number of threads
        '''

        def wrapper(instance, *args, **kwargs):
            parallelized = Parallel(n_jobs = -1)(func)
            out = parallelized(instance, *args, **kwargs)
            return out
            
        return wrapper if self.parallelize else func
