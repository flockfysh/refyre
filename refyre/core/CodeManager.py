import sys 
from pathlib import Path

class CodeManager:

    def __init__(self):
        self.module_dirs = []
        self.base_sys_paths = list(sys.path)

    def add(self, filepath):
        p = Path(filepath)
        if p.is_dir() and filepath not in sys.path:
            print('adding', filepath)

            self.module_dirs.append(filepath) 
            sys.path.append(filepath)
        elif p.is_file() and p.parent.as_posix() in sys.path:
            print('adding parent since it is file', p.parent.as_posix())

            self.module_dirs.append(p.parent.as_posix()) 
            sys.path.append(p.parent.as_posix())

    def clear(self):
        self.module_dirs.clear()


    
