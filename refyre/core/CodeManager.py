import sys 
from pathlib import Path

class CodeManager:

    def __init__(self):
        self.module_dirs = []
        self.base_sys_paths = list(sys.path)

    def add(self, filepath):
        p = Path(filepath)
        self.module_dirs.append(p.parent.as_posix()) 
        sys.path.append(p.parent.as_posix())

    def clear(self):
        self.module_dirs.clear()


    
