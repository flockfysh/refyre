from pathlib import Path 
from refyre.reader import PatternGenerator
import copy

class FileGraphNode:
    '''
        How the graph will be orchestrated:

        Problem: There may be multiple root "entry" directories the user many want to be 
        able to target.

        Solution: We abstract that away in the graph.

        We will have one virtual "root" node stringing together all the other entry points.
    '''
    def __init__(self, children = [], pattern = "", directory = "", type = "", name = "", is_root = False, flags = "", serialize = "", imports="", mode = "", link="", alias="", limit = ""):
        self.children = children

        self.pattern = pattern #fnmatch.translate(pattern) #Add this attribute to handle glob pattern recognition
        self.directory = directory
        self.type = type
        self.name = name
        self.is_root = is_root
        self.flags = flags
        self.serialize = serialize
        self.imports = imports
        self.mode = mode
        self.link = link
        self.alias = alias
        self.limit = limit


    def add_child(self, child):
        assert isinstance(child, FileGraphNode), "Children of FileGraphNode should only be FileGraphNodes"
        
        self.children.append(child)
    
    def add_children(self, children):
        for child in children:
            self.add_child(child)

    def is_root_dir(self):
        return self.is_root
        
    def __repr__(self):
        return f"FileGraphNode(children = {self.children}, pattern = {self.pattern}, directory = {self.directory}, type = {self.type}, name = {self.name}, is_root = {self.is_root}, flag = {self.flags}, serialize = {self.serialize}, imports = {self.imports}, mode = {self.mode})"
    
    def __copy__(self):
        new_obj = FileGraphNode()
        for k,v in vars(self).items():
            try:
                setattr(new_obj, k, copy.deepcopy(v))
            except Exception as e:
                print(e)

        return new_obj
    
    def copy(self):
        return self.__copy__()