import sys 
from pathlib import Path

class CodeManager:

    def __init__(self):
        self.module_dirs = []
        self.base_sys_paths = list(sys.path)

    def add(self, filepath):
        p = Path(filepath)
        self.module_dirs.append(str(p.parent)) 
        sys.path.append(str(p.parent))

    def clear(self):
        self.module_dirs.clear()


    
