from pathlib import Path

class AliasManager:

    def __init__(self):
        self.alias_dict = {}

    def add(self, alias, path, is_pathlib = False):
        self.alias_dict[alias] = Path(path) if not is_pathlib else path
    
    def __getitem__(self, key):
        return self.alias_dict[key]

    def __repr__(self):
        return f"AliasManager(aliases = {self.alias_dict})"
    
    def aliases(self):
        return self.alias_dict
    
    def clear(self):
        self.alias_dict.clear()