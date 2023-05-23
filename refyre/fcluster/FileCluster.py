from pathlib import Path
from functools import wraps
from refyre.utils import get_optimal_pattern
from refyre.reader import PatternGenerator
import re

#Copying / Deleting
import shutil

#Zipping
import zipfile

#GET/POST requests
import requests

#Iteration
from .FileClusterIterator import FileClusterIterator
from .AutoRefresher import AutoRefresher

def refresh(input_arr):
    '''
    A simple refresher method. This will handle variable conflicts.

    Whenever data is altered, all the invalid paths will drop out.

    Particularly useful for variables with overlapping data
    '''
    return [ v for v in set(input_arr) if v.exists() ]
        
def with_refresh(func):
    def refreshed(self, *args, **kwargs):
        self.values = refresh(self.values)
        return func(self, *args, **kwargs)

    return refreshed

class FileCluster:
    '''
        The workhorse of refyre. Variables do all of the heavylifting, harnessing
        the power of the data parsed through the fgraphs.

        Paradigms - any method that involves transporting data must be wrapped in the 
        refresher decorator method above. This will prevent overlapping variables from 
        incorrectly altering results from each other, as well as ensures that variables
        only contain valid data.
    '''

    #Counter to manage IDs
    GLOBAL_COUNTER = 0

    #Stores references to each FileCluster; in the future, this can be used for tracking & mem management
    clusters = []

    def __init__(self, input_paths = [], input_patterns = [], values = [], as_pathlib = False):
        assert len(input_paths) == len(input_patterns), "Uneven lengths for input paths and patterns"

        for pattern in input_patterns:
            print('add', pattern, PatternGenerator(pattern))
        self.values = self.__populate(input_paths, [ PatternGenerator(p) for p in input_patterns  ])

        #ID the variable
        self.id = FileCluster.GLOBAL_COUNTER
        FileCluster.GLOBAL_COUNTER += 1

        #Track the cluster
        FileCluster.clusters.append(self)
    
        #If the user didn't send the values as Pathlib objects already
        if not as_pathlib: 
            self.values += [ Path(pth) for pth in values ] 
        else:
            self.values += values

    
    def all_clusters(self):
        return FileCluster.clusters
    
    @AutoRefresher()
    def __add__(self, other):
        '''
            other - another FileCluster

            Returns a file cluster with all the combined values
        '''
        #Ensure the input_data is as desired
        assert type(other) == FileCluster

        new_values = self.values + other.values

        return FileCluster(input_paths = [], input_patterns = [], values = new_values, as_pathlib = True)
    
    @AutoRefresher()
    def __and__(self, other):
        '''
            other - another FileCluster

            Returns the intersection between the two FileClusters
        '''

        return FileCluster(input_paths = [], input_patterns = [], values = list(set(self.values).intersection(other.values)))
    
    @AutoRefresher()
    def __or__(self, other):
        '''
            other - another FileCluster

            Returns the union between two FileClusters
        '''

        return FileCluster(input_paths = [], input_patterns = [], values = list(set(self.values).union(other.values)))
    
    @AutoRefresher()
    def __sub__(self, other):
        '''
            other - another FileCluster

            Returns all the files that are exclusively in self
        '''

        return FileCluster(input_paths = [], input_patterns = [], values = [v for v in self.values if v not in other.values])

    @AutoRefresher()
    def __eq__(self, other):
        return set(self.values) == set(other.values)
    
    @AutoRefresher()
    def contains(self, other):
        return self & other == other

    def __populate(self, input_paths, input_patterns):
        '''
        Populates a variable, using the input paths and directories 
        '''

        ret = []
        for dir_path, pattern in zip(input_paths, input_patterns):
            print('pot', dir_path, pattern)
            for fl in Path(dir_path).iterdir():
                print(pattern, fl.name,re.search(r'{}'.format(pattern), fl.name) )
                if re.search(r'{}'.format(pattern), fl.name) and fl not in ret:
                    print('fl', fl, 'is match to ', dir_path, pattern)
                    ret.append(fl)
        
        return ret

    @AutoRefresher()
    def vals(self):
        '''
            Returns a Pathlib.Paths list of all
            filepaths
        '''
        return self.values
    
    @AutoRefresher()
    def dirs(self):
        '''
            Returns a Paths list of all parent directories
        '''
        return list(set([v.parent for v in self.values]))
    
    @AutoRefresher()
    def __repr__(self):
        return f"FileCluster(values = {self.values})"

    @AutoRefresher()
    def __len__(self):
        return len(self.values)

    @AutoRefresher()
    def __iter__(self):
        return 
    
    @AutoRefresher()
    def __getitem__(self, key):
        print(key)
        if isinstance(key, slice):
            return FileCluster(input_patterns = [] , input_paths = [], values = self.values[key.start:key.stop:key.step])
        elif isinstance(key, int):
            return FileCluster(input_patterns = [] , input_paths = [], values = self.values[key])

    #Update a map_func
    @AutoRefresher()
    def map(self, map_func):
        '''
        Input: 
            - map_func: a function to map each filepath. The mapping must take a filepath and return a filepath
        
        Return:
            - FileCluster object with the mapped values
        '''

        nvals = []
        for v in self.values:
            nvals.append(Path(map_func(v))) #Append a copy of the object to prevent object ref shenanigans
        
        p = FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)
        print(p)
        return p
    
    @AutoRefresher()
    def reduce(self, reducer_function):
        '''
        Input: 
            - reducer_function(a, b): Takes in two parameters that can be reduced into a third parameter
        
        Returns
            - the Result of the reduction, or None if the array is empty
        '''
        if len(self.values):
            a = self.values[0]

            for i in range(1, len(self.values)):
                a = reducer_function(a, self.values[i])

            return a
        
        return None

    def move(self, target_dir):
        '''
        Input: 
            - target_dir: the directory to which all files will be sent.
        
        Returns
            - FileCluster object with the new values 
        '''

        p = Path(target_dir)

        #If the directory doesn't actually exist or just isn't a directory, we return None
        if not p.exists() or not p.is_dir():
            return None

        @AutoRefresher(does_modify = True, mapper_func = lambda x : p / x.name)
        def exec_func(self, v):
            return self.map(v)

        return exec_func(self, lambda v : Path(v.as_posix()).rename(p / v.name))
    
    def copy(self, target_dir):
        '''
        Input: 
            - target_dir: the directory to which all files will be sent.
        
        Returns
            - FileCluster object with the new values 
        '''
        p = Path(target_dir)

        #If the directory doesn't actually exist or just isn't a directory, we return None
        if not p.exists() or not p.is_dir():
            return None

        def copy_func(v):
            shutil.copy(str(v), str(p / v.name))
            return p / v.name

        @AutoRefresher(does_modify = True, mapper_func = lambda x : p / x.name, instance = self)
        def exec_func(self):
            return self.map(copy_func) 

        return exec_func(self)
    
    def filter(self, filter_func):
        '''
        Input: 
            - filter_func: a function to filter out values, given an input of a filepath.
                - i.e, return False for any values we don't want to keep
        
        Return:
            - FileCluster object with the filtered values
        '''


        nvals = []
        @AutoRefresher(does_modify = True, does_filter = True, filter_func = filter_func, instance = self)
        def work(self):
            for v in self.values:
                if filter_func(v):
                    nvals.append(Path(v.as_posix())) #Append a copy of the object to prevent object ref shenanigans
        
        work(self)
        return FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)
    
    def delete(self):
        '''
        Deletes all the files in the variable. 

        Return:
            - Empty FileCluster object
        '''

        @AutoRefresher(does_modify = True, does_filter = True, filter_func = lambda x : False)
        def work(self):
            for fl in self.values:
                if fl.is_dir():
                    shutil.rmtree(fl.as_posix())
                elif fl.is_file():
                    fl.unlink()

        work(self)
        return FileCluster(input_patterns = [], input_paths = [], values = [])

    def rename(self, rename_function):
        '''
            rename_function: a function that takes an integer as an input 
        '''

        i = -1
        def sample(x):
            nonlocal i
            i += 1
            return x.parent / rename_function(i)

        @AutoRefresher(does_modify = True, mapper_func = sample)
        def work(self):
            nvals = []
            for i, v in enumerate(self.values):
                print('renaming', v,v.parent / rename_function(i) )
                nvals.append(Path(v.as_posix()).rename(v.parent / rename_function(i)))
            return nvals

        nvals = work(self)
        return FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)

    @AutoRefresher()
    def zip(self, save_dir = '.', save_name = "out.zip"):
        '''
        Zips all the files into a single zip.
        '''

        save_p = Path(save_dir) / save_name

        copied = self.copy(save_dir)

        with zipfile.ZipFile(save_p.as_posix(), 'w') as zipMe:        
            for fl in copied.values:
                zipMe.write(fl.as_posix(), compress_type=zipfile.ZIP_DEFLATED)
        
        assert save_p.exists(), "For some reason, the newly created zip file does not exist"

        copied.delete()
        return FileCluster(input_patterns = [], input_paths = [], values = [save_p], as_pathlib = True)

    @AutoRefresher()
    def post(self, url, additional_data, payload_name):
        '''
        Uses the requests library to send a post request to the url, 
        alongside the additional payload parameters you specify. All the data 
        you want to push through is sent as a zip 

            url: Str link to the API endpoint
            additional_data: a dict to any other metadata you want to ferry across
            payload_name: what you want to name the zip going across


        Return type: the Response object returned from the requests.get() call
        '''

        #Zip all the files up to send
        zipped = self.zip()
        zipped_fp = zipped.vals()[0].as_posix()

        resp = None
        with open(zipped_fp, "rb") as f:
            resp = requests.post(url = url, params = additional_data, files = { payload_name : f })

        #Delete the intermediate zip we constructed
        zipped.delete()

        return resp 

    