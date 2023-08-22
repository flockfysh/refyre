from pathlib import Path
from functools import wraps
from refyre.utils import get_optimal_pattern, optional_dependencies
from refyre.config import logger
from refyre.reader import PatternGenerator
import re

#Copying / Deleting
import shutil

#Iteration
from .ClusterIterator import FileClusterIterator
from .Broadcast import Broadcaster
from .Cache import AutoCache

#Copy
import copy

#Zip
import zipfile


#Store a weak reference to the object
import weakref


def handle_file_conflict(destination_path):
    if not destination_path.exists():
        return destination_path

    base_name = destination_path.stem
    suffix = destination_path.suffix
    directory = destination_path.parent

    index = 1
    while True:
        new_name = f"{base_name}({index}){suffix}"
        new_path = directory / new_name
        if not new_path.exists():
            return new_path
        index += 1

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
    clusters = {}

    def __init__(self, input_paths = [], input_patterns = [], values = [], as_pathlib = False, recursive = False):
        assert len(input_paths) == len(input_patterns), "Uneven lengths for input paths and patterns"
        logger.debug('init')

        for pattern in input_patterns:
            logger.debug(f'add {pattern} {PatternGenerator(pattern)}')
        self.values = self.__populate(input_paths, [ PatternGenerator(p) for p in input_patterns  ], recursive = recursive)

        #ID the variable
        self.id = FileCluster.GLOBAL_COUNTER
        FileCluster.GLOBAL_COUNTER += 1

        #Track the cluster without affecting garbage collection
        self.weak_ref = weakref.ref(self)
        FileCluster.clusters[self.id] = self.weak_ref

        #Setup a cache dir
        self.cache_dir = '.refyre_cache'
    
        #If the user didn't send the values as Pathlib objects already
        if not as_pathlib: 
            self.values += [ Path(pth) for pth in values ]
        else:
            self.values += values

        self.values = sorted(self.values)
        #Track variable on broadcaster
        Broadcaster.add(self.id, self.values)

    def all_clusters(self):
        return FileCluster.clusters

    def __del__(self):
        if self.id in FileCluster.clusters:
            FileCluster.clusters.pop(self.id)
        Broadcaster.release(self.id)

    
    @classmethod
    def cleanup(cls):
        for k in list(FileCluster.clusters):
            obj = FileCluster.clusters[k]
            if obj() is None:
                FileCluster.clusters.pop(k)

    @classmethod
    def wipe(cls):
        for k in list(FileCluster.clusters):
            logger.debug(f'wiping {k}')
            obj = FileCluster.clusters[k]()
            if obj is not None:
                logger.debug(f'deleting {k}')
                del obj 
        
        FileCluster.GLOBAL_COUNTER = 0
        Broadcaster.clear()
        FileCluster.clusters.clear()

    def __add__(self, other):
        '''
            other - another FileCluster

            Returns a file cluster with all the combined values
        '''
        #Ensure the input_data is as desired
        assert type(other) == FileCluster

        new_values = self.values + other.values

        return FileCluster(input_paths = [], input_patterns = [], values = new_values, as_pathlib = True)
    
    def __and__(self, other):
        '''
            other - another FileCluster

            Returns the intersection between the two FileClusters
        '''

        return FileCluster(input_paths = [], input_patterns = [], values = list(set(self.values).intersection(other.values)))
    
    def __or__(self, other):
        '''
            other - another FileCluster

            Returns the union between two FileClusters
        '''

        return FileCluster(input_paths = [], input_patterns = [], values = list(set(self.values).union(other.values)))
    
    def __xor__(self, other):
        '''
            other - another FileCluster

            Returns the exclusive or between the two FileClusters
        '''
        return FileCluster(input_paths = [], input_patterns = [], values = list(set(self.values) ^ set(other.values)))
    
    def __sub__(self, other):
        '''
            other - another FileCluster

            Returns all the files that are exclusively in self
        '''

        return FileCluster(input_paths = [], input_patterns = [], values = [v for v in self.values if v not in other.values])

    def __eq__(self, other):
        if other is None or type(other) != FileCluster:
            return False
        return set(self.values) == set(other.values)
    
    def __contains__(self, other):
        return self & other == other

    def __populate(self, input_paths, input_patterns, recursive = False):
        '''
        Populates a variable, using the input paths and directories 
        '''

        ret = []
        for dir_path, pattern in zip(input_paths, input_patterns):
            logger.debug(f'pot {dir_path} {pattern}')

            it = sorted(Path(dir_path).iterdir()) if not recursive else sorted(Path(dir_path).glob('**/*'))
            for fl in it:
                if re.search(r'{}'.format(pattern), fl.name) and fl not in ret:
                    ret.append(fl)
        
        return ret

    def vals(self):
        '''
            Returns a Pathlib.Paths list of all
            filepaths
        '''
        return self.values
    
    def item(self):
        '''
            Returns a Pathlib.Paths list of all
            filepaths
        '''
        return self.values[0]

    def dirs(self):
        '''
            Returns a FileCluster of all parent directories
        '''
        return FileCluster(values = list(dict.fromkeys([v.parent for v in self.values])), as_pathlib = True)
    
    def __repr__(self):
        return f"FileCluster(values = {self.values})"

    def __len__(self):
        return len(self.values)

    def __iter__(self):
        return FileClusterIterator(self)

    def __copy__(self):
        return FileCluster(values = self.values, as_pathlib = True)
    
    def __deepcopy__(self):
        return FileCluster(values = [Path(p) for p in self.values], as_pathlib = True)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return FileCluster(input_patterns = [] , input_paths = [], values = self.values[key.start:key.stop:key.step], as_pathlib = True)
        elif isinstance(key, int):
            return FileCluster(input_patterns = [] , input_paths = [], values = [self.values[key]], as_pathlib = True)

    @Broadcaster()
    def move(self, target_dir, conflict_function = handle_file_conflict):
        """
        The above code defines functions for moving, copying, and deleting files in a directory, with
        options for handling conflicts and broadcasting changes.
        
        :param target_dir: The directory to which files will be moved or copied
        :param conflict_function: conflict_function is a function that takes in a Path object
            representing a file and returns a Path object representing the destination file path. This
            function is used in the move and copy methods to handle file conflicts, such as when a file with
            the same name already exists in the target directory. The default conflict
        :return: The `move` method returns a tuple containing a list of changes made (as tuples of old
        and new file paths) and a new `FileCluster` object with updated values.
        """


        p = Path(target_dir)

        #If the directory doesn't actually exist or just isn't a directory, we return None
        if not p.exists() or not p.is_dir():
            return None

        nvals = []
        changes = []

        for v in self.values:
            logger.debug(f'{v.parent}, {p}')
            if v.parent != p:
                logger.debug('in')
                dest = conflict_function(p / v.name)

                #if dest is None, we ignore it
                if dest:
                    logger.debug(f'{str(v)}, {str(dest)}')
                    shutil.move(str(v), str(dest))
                    changes.append((str(v), str(dest)))
                    nvals.append(Path(dest))
            else:
                logger.debug('else')
                logger.debug(str(v))
                changes.append((str(v), str(v)))
                nvals.append(Path(v))
            
        return changes, FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)
    
    def copy(self, target_dir, conflict_function = handle_file_conflict):
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
        
        nvals = []
        for v in self.values:
            dest = conflict_function(p / v.name)

            #if dest is None, we ignore it
            if dest:
                shutil.copy(str(v), str(dest))
                nvals.append(Path(dest))
            
        return FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)

    @Broadcaster()
    def delete(self):
        """
        The function deletes all files in a FileCluster object and returns an empty object while keeping
        track of the changes made.
        :return: a tuple containing two elements: a list of changes made during the deletion process and
        an empty FileCluster object.
        """
        changes = []
        for fl in self.values:
            if fl.is_dir():
                shutil.rmtree(str(fl))
                changes.append((str(fl), None))
            elif fl.is_file():
                fl.unlink()
                changes.append((str(fl), None))


        return changes, FileCluster(input_patterns = [], input_paths = [], values = [])

    @Broadcaster()
    def rename(self, rename_function):
        """
        This function renames files in a FileCluster object using a provided renaming function.
        
        :param rename_function: The `rename_function` parameter is a function that takes an integer as
            an input and returns a string. This function is used to rename the files in the `values` list of
            the `FileCluster` object. The integer input to the function is the index of the file in the
            `values`
        :return: a tuple containing two values: 
        1. A list of tuples representing the changes made during the renaming process. Each tuple
        contains two strings: the original path and the new path.
        2. A new instance of the FileCluster class with the updated values after the renaming process.
        """
        
        nvals = []
        changes = []
        for i, v in enumerate(self.values):
            logger.debug(f'renaming, {v},{v.parent / rename_function(i)}')
            nvals.append(Path(v).rename(v.parent / rename_function(i)))
            changes.append((str(v), str(nvals[-1])))

        return changes, FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)

    def zip(self, save_dir = '.', save_name = "out.zip", conflict_function = handle_file_conflict):
        """
        This function zips all the files in a directory into a single zip file.
        
        :param save_dir: The directory where the zip file will be saved. If not specified, it will
        default to the current working directory, defaults to . (optional)
        :param save_name: The name of the zip file that will be created, defaults to out.zip (optional)
        :param conflict_function: The conflict_function parameter is a function that is used to handle
        conflicts that may arise when trying to save the zip file to the specified directory. It takes
        in the path of the file that is being saved and returns a new path if there is a conflict with
        an existing file in the directory. If no
        :return: a `FileCluster` object that contains the path to the newly created zip file.
        """

        save_p = Path(save_dir) / save_name

        copied = self.copy(save_dir)


        save_p = handle_file_conflict(save_p)
        with zipfile.ZipFile(str(save_p), 'w') as zipMe:        
            for fl in copied.values:
                zipMe.write(str(fl), compress_type=zipfile.ZIP_DEFLATED)
        
        assert save_p.exists(), "For some reason, the newly created zip file does not exist"

        copied.delete()

        return FileCluster(input_patterns = [], input_paths = [], values = [save_p], as_pathlib = True)

    def post(self, url, additional_data, payload_name):
        """
        This function sends a post request to a specified API endpoint with additional payload parameters
        and returns the response object.
        
        :param url: The link to the API endpoint where the post request will be sent
        :param additional_data: a dictionary containing any additional metadata you want to send along with
        the request. This could include things like authentication tokens or other parameters required by
        the API endpoint you are sending the request to
        :param payload_name: The name you want to give to the zip file that will be sent as part of the POST
        request
        :return: the Response object returned from the requests.post() call.
        """

        with optional_dependencies('warn'):
            #GET/POST requests
            import requests
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
            zipped_fp = str(zipped.item())

            resp = None
            with open(zipped_fp, "rb") as f:
                resp = requests.post(url = url, params = additional_data, files = { payload_name : f })

            #Delete the intermediate zip we constructed
            zipped.delete()

            return resp 

    #DO NOT ADD AN AUTOREFRESHER DECORATOR HERE --> It will add a middleman to move() and copy() that will alter results
    def map(self, map_func):
        """
        This function maps each filepath in a FileCluster object using a given function and returns a
        new FileCluster object with the mapped values.
        
        :param map_func: `map_func` is a function that takes a filepath as input and returns a filepath
        as output. This function is used to map each filepath in the `values` attribute of a
        `FileCluster` object. The resulting `FileCluster` object will have the same structure as the
        original one, but
        :return: A new FileCluster object with the mapped values.
        """
        nvals = []
        for v in self.values:
            nvals.append(Path(map_func(v))) #Append a copy of the object to prevent object ref shenanigans
        
        p = FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)
        return p
    
     
    def reduce(self, reducer_function):
        """
        The reduce function takes in a reducer function and returns the result of reducing the values in
        the array using the reducer function, or None if the array is empty.
        
        :param reducer_function: A function that takes in two parameters and returns a third parameter
        that can be used to reduce a list of values into a single value. This function is used in the
        reduce method of a class to perform the reduction operation on the list of values stored in the
        class instance
        :return: the result of the reduction of the values in the array using the given reducer
        function. If the array is empty, it returns None.
        """
        if len(self.values):
            a = self.values[0]

            for i in range(1, len(self.values)):
                a = reducer_function(a, self.values[i])

            return a
        
        return None
    
    def filter(self, filter_func):
        """
        This function takes a filter function as input and returns a new FileCluster object with values
        filtered based on the input function.
        
        :param filter_func: filter_func is a function that takes a filepath as input and returns a boolean
        value. It is used to filter out values that we don't want to keep in a FileCluster object. If the
        function returns True for a given filepath, it will be included in the filtered FileCluster object.
        If it
        :return: A FileCluster object with the filtered values.
        """

        nvals = []
        for v in self.values:
            if filter_func(v):
                nvals.append(Path(v)) #Append a copy of the object to prevent object ref shenanigans
        
        return FileCluster(input_patterns = [], input_paths = [], values = nvals, as_pathlib = True)

    def clone(self):
        """
        The function returns a deep clone of the current object.
        :return: A deep clone of the current object is being returned.
        """

        return self.__deepcopy__()

    def decompress(self, complete = False):
        """
        Takes any folders within the values, and replaces them with all the items in the folder

        If complete is set to True, then it will recursively empty all files 
        """
        nvals = []
        for pth in self.values:
            if pth.is_dir():
                nvals.extend([*pth.iterdir()] if not complete else [*pth.rglob('**/*')])
            elif pth.is_file():
                nvals.append(pth)
        
        return FileCluster(values = nvals, as_pathlib = True)
            
    def cache(self):
        """
        Saves all the files to cache
        """

        ca = AutoCache(self.cache_dir)
        return ca.cache(self)
    
    def decache(self):
        ca = AutoCache(self.cache_dir)
        return ca.decache(self)
    
    def cached(self):
        """
        Returns all the FileCluster files in the cluster that are currently cached
        """
        nvals = []
        ca = AutoCache(self.cache_dir)

        for v in self.values:
            if ca.contains(str(v)):
                nvals.append(v)
            
        return FileCluster(values = nvals, as_pathlib = True)
    
    def unlink(self):
        """
        Returns a FileCluster detached from the Broadcaster system
        """

        f = self.clone()
        Broadcaster.unlink(f.id)
        return f
    
    def relink(self):
        """
        Reconnect the FileCluster to the broadcaster
        """
        return self.clone()

    def filesize(self, format = "bytes"):
        """
        Returns the total file size, in bytes 
        """
        total_size = 0.0

        for pth in self.values:
            if pth.is_dir():
                total_size += sum([p.stat().st_size for p in Path(pth).rglob('*')])
            elif pth.is_file():
                total_size += pth.stat().st_size

        return total_size

    def filecount(self):
        """
        Returns the total number of files over all folders
        """
        total_files = 0

        for pth in self.values:
            if pth.is_dir():
                total_files += len([p.stat().st_size for p in Path(pth).rglob('*')])
            elif pth.is_file():
                total_files += 1
        
        return total_files