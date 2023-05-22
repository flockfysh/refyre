from pathlib import Path  

def insert(fdct, k, v):
    if k not in fdct:
        fdct[k] = set()
    
    fdct[k].add(v)

class AutoRefresher:
    '''
    The AutoRefresher acts as a failsafe, gatekeeping mechanism for 
    the FileCluster.

    Here's what it does - 
        - Ensures that the variables contain unique, valid files. Any duplicates or nonexistent paths are removed.
        - Updates any updated paths for overlapping variables; i.e. if you change a variable's data and move some files, other variables that may share the
        same filepaths will have their filepaths updated

    AutoRefresher currently supports two modes - 
    1. "preserve" - This is the default mode. If any changes are made in one variable's contents, the updates are propogated to the rest of the vars.
    2. "optimize_single_real" - The most optimized, this mode deletes any paths in the variable that no longer exist, and ensures the paths are purely unique

    '''
    REFRESHER_MODE = 'preserve'
    VALID_MODES = ['preserve']

    #A global dictionary to manage filepath movements
    files_dict = {} #Maps filepath strings to new strings. If a filepath is expected to be gone, it will contain the value None

    def __init__(self, *a, **kw):
        self.conf_args = a
        self.conf_kw = kw
        
        print("init autorefresh", self.conf_args, self.conf_kw)
       
    def __call__(self, func):
        
        if AutoRefresher.REFRESHER_MODE == 'preserve':


            def wrapper(instance, *args, **kwargs):

                #Update & Delete any paths using the files_dict
                nvals = [] 
                fdct = AutoRefresher.files_dict

                #Remove all instances of var.id from dict
                for k in fdct:
                    fdct[k].discard(instance.id)

                clusters = instance.all_clusters()

                for v in instance.values:
                    if v not in nvals and "does_modify" in self.conf_kw and self.conf_kw["does_modify"]:
                        if "mapper_func" in self.conf_kw:

                            '''
                                How can a file conflict occur?

                                No matter what, if the mapped file already exists in the dictionary, then we 
                                say a file conflict exists. 

                                This is quite a strong statement, but renaming a file (false positive) is a lot
                                safer than losing the file entirely (false negative) 
                            '''
                            #Check and handle file conflicts

                            i = 0
                            potential_candidate = v
                            while (self.conf_kw["mapper_func"](potential_candidate)).as_posix() in fdct:
                                print('file conflict', potential_candidate, self.conf_kw["mapper_func"](potential_candidate))
                                i += 1
                                potential_candidate = self.conflict_filename(potential_candidate.parent, potential_candidate.stem, potential_candidate.suffix, i) 
                            
                            print(potential_candidate, fdct, 'clearly, no file exists')

                            if potential_candidate != v:
                                #Move all relevant ids to the filename

                                #Remove all the old values
                                for cluster_id in fdct[v.as_posix()]:
                                    cluster_var = clusters[cluster_id]
                                    cluster_var.values = [p for p in cluster_var.values if p.as_posix() != v.as_posix()] + [Path(potential_candidate.as_posix())]

                                o_set = fdct[v.as_posix()]
                                
                                assert potential_candidate.as_posix() not in fdct, "New candidate is somehow in our dictionary"

                                #Create a new set
                                fdct[self.conf_kw["mapper_func"](potential_candidate).as_posix()] = set()

                                #Update dict
                                for n in o_set:
                                    fdct[self.conf_kw["mapper_func"](potential_candidate).as_posix()].add(n)

                                #Remove the old set
                                fdct.pop(v.as_posix(), None)

                                #Rename the file
                                v.rename(potential_candidate)
                                assert potential_candidate.exists(), "New candidate doesnt exist after renaming"

                            #update dict, and add to nvals

                            insert(fdct, self.conf_kw["mapper_func"](potential_candidate).as_posix(), instance.id)
                            nvals.append(potential_candidate)
                        
                        if "does_filter" in self.conf_kw and self.conf_kw["does_filter"] and "filter_func" in self.conf_kw:
                            
                            if not self.conf_kw["filter_func"](v):
                                print('want filter', v)

                                #Delete across all variables
                                for cluster_id in fdct[v.as_posix()]:
                                    cluster_var = clusters[cluster_id]
                                    cluster_var.values = [p for p in cluster_var.values if p.as_posix() != v.as_posix()]
                                
                                #Delete the dict entry
                                fdct.pop(v.as_posix(), None)
                            
                            #Otherwise, it's just a normal file, treat it as such
                            else:
                                insert(fdct, v.as_posix(), instance.id)
                                nvals.append(v)

                    elif v not in nvals: 

                        #Add the id 
                        insert(fdct, v.as_posix(), instance.id)
                        nvals.append(v)

                #Add any expected filepath changes

                #print('returned nvals', nvals)
                instance.values = [v for v in list(set(nvals)) if v.exists() ]
                return func(instance, *args, **kwargs)
            
        


        return wrapper
        
    def set_mode(new_mode):

        if new_mode.lower().strip() not in AutoRefresher.VALID_MODES:
            raise Exception('Invalid mode specified')

        AutoRefresher.REFRESHER_MODE = new_mode
        print('New mode set to ', AutoRefresher.REFRESHER_MODE)
    
    def preserve(self, input_arr):
        '''
        A simple refresher method. This will handle variable conflicts.

        Whenever data is altered, all the invalid paths will drop out.

        Particularly useful for variables with overlapping data
        '''
        return [ v for v in set(input_arr) if v.exists() ]
    
    def get_latest(self, p):

        if AutoRefresher.files_dict[p][1] == None or self.bad_next(p):
            return p 
        
        d = self.get_latest(AutoRefresher.files_dict[p][1])
        if d != p:
            AutoRefresher.files_dict[p][1] = d
        else:
            AutoRefresher.files_dict[p][1] = None

        return d
        
    def bad_next(self, p):
        return AutoRefresher.files_dict[p][1] not in AutoRefresher.files_dict or not AutoRefresher.files_dict[AutoRefresher.files_dict[p][1]][2]

    
    def resolve_file_conflicts(self, input_arr, mapper_func):
        return [self.handle_file_conflict(fl, mapper_func) for fl in set(input_arr)]

    def handle_file_conflict(self, fl, mapper_func):
        '''
            Function to update filnames to resolve 
            potential file conflicts
        '''
        if not mapper_func(fl).exists() or (mapper_func(fl).exists() and mapper_func(fl) == fl):
            print('ret post handle', fl, fl.exists(), 'which would be mapped to ', mapper_func(fl))
            return fl
        
        i = 0
        potential_candidate = fl
        while mapper_func(potential_candidate).exists():
            i += 1
            potential_candidate = self.conflict_filename(fl.parent, fl.stem, fl.suffix, i)
            
        fl.rename(potential_candidate)
        print('ret post handle 2', fl, fl.exists(), potential_candidate, potential_candidate.exists())
        return potential_candidate
        
    
    def conflict_filename(self, parent, fl_name, fl_stem, i):
        return parent / f"{fl_name}({i}){fl_stem}"


