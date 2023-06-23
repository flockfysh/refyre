from pathlib import Path
from itertools import product
from refyre.config import logger

from .Cluster import FileCluster
from .ClusterIterator import FileClusterIterator

#Store a weak reference to the object
import weakref

class AssociationCluster:

    #Counter to manage IDs
    GLOBAL_COUNTER = 0

    #Stores references to each AssociationCluster; in the future, this can be used for tracking & mem management
    clusters = {}

    def __init__(self, starting_vals = None, mapper_function = lambda x : x, one_to_one = False , as_pathlib = False, input_vars = []):
        self.values = []


        if starting_vals:
            out = []
            if not as_pathlib:
                for p in starting_vals:
                    t = (Path(v) for v in p)
                    out += t
            
            self.values += out

        #ID the variable
        self.id = AssociationCluster.GLOBAL_COUNTER
        AssociationCluster.GLOBAL_COUNTER += 1

        #Track the cluster without affecting garbage collection
        self.weak_ref = weakref.ref(self)
        AssociationCluster.clusters[self.id] = self.weak_ref

        if input_vars:
            input_vars = [v.vals() for v in input_vars]
            iter_form = product(*input_vars) if not one_to_one else zip(*input_vars)
            for permutation in iter_form:
                if mapper_function(permutation):
                    self.values.append(permutation)
        
    
    def clusterify(self, mapper_function = None):
        single_values = []

        for val_set in self.values:
            if mapper_function:
                m = mapper_func(*val_set)
                if isinstance(m, list):
                    single_values.extend(m)
                else:
                    single_values.append(m)
            else:
                for v in val_set:
                    single_values.append(v) 
        
        return FileCluster(values = single_values, as_pathlib = True)
        
    def vals(self):
        return self.values

    def __len__(self):
        return len(self.values) 
    
    def __contains__(self, k):
        return k in self.values

    def __iter__(self):
        return FileClusterIterator(self)

    def __repr__(self):
        return f"AssociationCluster(values = {self.values})"

    def __copy__(self):
        return AssociationCluster(values = self.values, as_pathlib = True)
    
    def __getitem__(self, key):
        if isinstance(key, slice):
            return AssociationCluster(values = self.values[key.start:key.stop:key.step], as_pathlib = True)
        elif isinstance(key, int):
            return AssociationCluster(values = [self.values[key]], as_pathlib = True)
    
    def __del__(self):
        logger.debug(f'deleting {self.id}')
        if self.id in AssociationCluster.clusters:
            AssociationCluster.clusters.pop(self.id)
    
    @classmethod
    def cleanup(cls):
        for k in list(AssociationCluster.clusters):
            obj = AssociationCluster.clusters[k]
            if obj() is None:
                AssociationCluster.clusters.pop(k)

    def all_clusters(self):
        return AssociationCluster.clusters

    def __eq__(self, other):
        if other is None or type(other) != AssociationCluster:
            return False
        return set(self.values) == set(other.values)
    
    def __add__(self, other):
        '''
            other - another AssociationCluster

            Returns a file cluster with all the combined values
        '''
        #Ensure the input_data is as desired
        assert type(other) == AssociationCluster

        new_values = self.values + other.values

        return AssociationCluster(values = new_values, as_pathlib = True)