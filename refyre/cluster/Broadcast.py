from pathlib import Path  
from refyre.config import logger

def insert(fdct, k, v):
    if k not in fdct:
        fdct[k] = set()
    
    fdct[k].add(v)

class Broadcaster:

    files_dict = {}
    ignore_list = []

    def __init__(self, *a, **kw):
        self.conf_args = a 
        self.conf_kw   = kw
    
    @classmethod
    def clear(cls):
        cls.files_dict.clear()

    @classmethod
    def add(cls, id, cluster_vals):
        for v in cluster_vals:
            insert(cls.files_dict, str(v), id) 

        
    @classmethod
    def release(cls, cluster_id):
        logger.debug(f'released {cluster_id}')
        for k in cls.files_dict:
            logger.debug(f'{k}, {cluster_id}, {cls.files_dict[k]}')
            cls.files_dict[k].discard(cluster_id)

        if cluster_id in cls.ignore_list:
            cls.ignore_list.remove(cluster_id)

    @classmethod
    def unlink(cls, cluster_id):
        if cluster_id not in cls.ignore_list:
            cls.ignore_list.append(cluster_id)
        

    def __call__(self, func):
        
        def wrapper(instance, *args, **kwargs):
            '''
                change_arr: List[Tuple(Str, Str)]
                    - Lists the Str that the path started out as, and what it became. 
                    - If second tuple None, it implies a path was deleted

            '''

            if instance.id not in self.ignore_list:
                instance.values = [v for v in list(dict.fromkeys(instance.values)) if v.exists() ]

            change_arr, out = func(instance, *args, **kwargs)

            if instance.id in self.ignore_list:
                return out


            logger.debug(f"CHANGE {change_arr}")
            logger.debug(out)

            clusters = instance.all_clusters()

            logger.debug(self.files_dict)
            self.files_dict = {k:self.files_dict[k] for k in self.files_dict if len(self.files_dict[k]) > 0}

            for before, after in change_arr:

                assert before != None 

                if before not in self.files_dict:
                    continue

                #Extract the dictionary values for before
                before_vals = self.files_dict.pop(before)

                #Assert no instance of after exists (otherwise a duplicate) (either None, or not in files_dict)
                logger.debug(f'{before}, {after}, {self.files_dict}')

                #Move everything to after & make the mods
                if after:
                    logger.debug('after not none')
                    if after in self.files_dict:
                        logger.debug(f'heeres {self.files_dict[after]}')
                    self.files_dict[after] = before_vals.union(self.files_dict[after]) if after in self.files_dict else before_vals
                    for cluster_id in before_vals:
                        cluster = clusters[cluster_id]()
                        if cluster_id != instance.id and Path(before) in cluster.values:
                            cluster.values[cluster.values.index(Path(before))] = Path(after)
                        
                else:
                    for cluster_id in before_vals:
                        if cluster_id != instance.id:
                            cluster = clusters[cluster_id]()
                            cluster.values = [v for v in cluster.values if str(v) != before] 

            self.files_dict = {k:self.files_dict[k] for k in self.files_dict if len(self.files_dict[k]) > 0 and Path(k).exists()}
            Broadcaster.files_dict = self.files_dict

            instance.values = [v for v in list(dict.fromkeys(instance.values)) if v.exists() ]
            logger.debug(f"RETURNED {instance.values} {self.files_dict} {Broadcaster.files_dict}")

            return out
            
        return wrapper 
