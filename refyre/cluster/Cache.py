from pathlib import Path
from refyre.config import logger
import json
import shutil


class AutoCache:

    cache_files = set()

    def __init__(self, cache_dir = '.refyre_cache'):
        self.cache_dir = Path(cache_dir)
        
        self.cache_dir.mkdir(parents = True, exist_ok = True)

        if (self.cache_dir / '.refyre_cache.json').exists():
            self.cache_files = set(self.load(self.cache_dir / '.refyre_cache.json'))
        else:
            self.cache_files = set()


    def cache(self, var):

        #Delete all the files in the cache with the same names
        for fl in var:
            if fl.name in self.cache_files:
                if fl.is_dir():
                    shutil.rmtree(str(self.cache_dir / fl.name))
                elif fl.is_file():
                    (self.cache_dir / fl.name).unlink()

        logger.debug(f'CACHED {self.cache_files}')
        for fl in var:
            if fl.name not in self.cache_files:
                self.cache_files.add(fl.name)

        logger.debug(f'CACHED {self.cache_files}')
        
        return var.copy(str(self.cache_dir))
    
    def decache(self, var, dest_dir = '.'):
        #Delete all the files in the cache with the same names
        nvals = []
        for fl in var:
            if fl.name in self.cache_files:
                nvals.append(self.cache_dir / fl.name)
                self.cache_files.discard(fl.name)

        from .Cluster import FileCluster
        return FileCluster(values = nvals, as_pathlib = True).move(dest_dir)

    def load(self, fp):
        with open(str(fp), 'r') as f:
            dct = json.load(f)
        return dct['files']

    def save(self, pth = None):
        if self.cache_dir.exists():
            with open(str(self.cache_dir / '.refyre_cache.json') if not pth else pth, 'w') as f:
                json.dump({'files' : list(self.cache_files) }, f)

    def contains(self, fp):
        return Path(fp).name in self.cache_files
        
    def __del__(self):
        self.save()
    
    @classmethod
    def obliterate(cls, cache_instance):
        """
        Automatically wipe the entire cache object
        """
        shutil.rmtree(str(cache_instance.cache_dir))
    
    def __len__(self):
        return len(self.cache_files) - 1

