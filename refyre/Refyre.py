from refyre.fgraph import FileGraph
from refyre.reader import Lexer
from refyre.reader import Parser
from refyre.fcluster import FileCluster

#pathlib
from pathlib import Path

#Garbage collection
import gc

#Regex
import re

#Deleting
import shutil

class Refyre:

    def __init__(self, input_specs = None, output_specs = None):
        '''
            input_specs: A List[Str] of filepaths to the various specs refyre will target
        '''

        self.variables = {}
        self.file_graph = FileGraph()

        if input_specs:
            assert isinstance(input_specs, list)
            for spec in input_specs:
                self.add_spec(spec)
        
        if output_specs:
            assert isinstance(output_specs, list)
            for spec in output_specs:
                self.create_spec(spec)

    def __getitem__(self, key):
        '''
            The refyre variables ("FileClusters") can be
            internally referred to through the Refyre object
        '''
        return self.variables[key]
    

    #The Five Fundamental Operations of Refyre
    def __construct(self, input_path):
        '''
            Construct Operation:
                - Receives an input spec, and creates an fgraph
        '''
        return Parser.parse(Lexer.lex(input_path))

    def __verify(self, node, path = ""):
        '''
            A simple verification method to ensure the basic integrity of a fgraph.

            This method ONLY CHECKS TO SEE IF DIRECTORIES ARE LEGIT. It does nada mas.

            Assumptions:
                - If a node is root, it will be the base directory, and the absolute path will be taken from there.
        '''
        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory

        print('Testing to see if ', new_path, 'exists')
        if not new_path.exists():
            return False
        
        new_path = new_path.as_posix()
        for child in node.children:
            if not self.__verify(child, new_path):
                return False

        return True
    

    def __activate(self, node , path = "", mode = "normal"):
        '''
            Activates an fgraph. 
            This means that all variables inside will be collected and factored into the refyre instance.

            The mode parameter defines the behaviour of the method.

            mode = "normal" means normal activation. This is done for input specs, a.k.a. for specs from which we want to 
            COLLECT (retrieve data)

            mode = "deploy" kickstarts deploy activation. Do this for any spec in which we want to TRANSFER / OUTPUT variable
            data somewhere.
        '''

        #Updating the path
        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory

        if not new_path.exists():
            raise Exception(f"Weird issue caught during activation ... an invalid path appeared - {new_path}")

        new_path = new_path.as_posix()

        if node.name != "":
            self.__parse_var(node, new_path, mode)

        for child in node.children:
            self.__activate(child, new_path, mode)

    
    def __output(self, node, path = "", mode = "copy"):
        '''
            Outputs an fgraph. 

            By default, this method performs an in-place generation of the file spec. In other words, no directories will be deleted, and it'll try to create 
            any folders that are missing.

            However, if you want the directory structure in the area to look exactly as mentioned in the output spec (no other dirs), you can specify the flag *c 
            using the flags attribute.
        '''
        #Updating the path
        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory

        self.__create_output(node, new_path, mode)
        new_path = new_path.as_posix()

        for child in node.children:
            self.__output(child, new_path, mode)
        

    def __clear(self):
        '''
            Wipes the refyre instance clean.
        '''

        self.variables.clear()
        self.file_graph = FileGraph()
        gc.collect()

    def __parse_var(self, node, path, mode):
        '''
        Parses all the options in the "names" attribute.

        I expect this method to blow up as this codebase grows (it's an options methods, and you never can have enough options!), 
        so once this goes over 100 lines, we'll move
        it into the fgraph directory.
        '''

        if mode == "normal":

            #Currently, this operator pattern supports only + and "" (appending and defining)
            options_pattern = r'^(\+)?(.*)$' 

            match = re.match(options_pattern, node.name)
            operator = match.group(1) or ""
            name = match.group(2)

            #In this case, the user wants to define a variable
            if operator == "" or (operator == "+" and name not in self.variables):
                self.variables[name] = FileCluster(input_paths = [path], input_patterns = [node.pattern])

            elif operator == "+":
                self.variables[name] += FileCluster(input_paths = [path], input_patterns = [node.pattern])

    def __create_output(self, node, path, mode):
        '''
        Parses all the options in the "names" attribute.

        I expect this method to blow up as this codebase grows (it's an options methods, and you never can have enough options!), 
        so once this goes over 100 lines, we'll move
        it into the fgraph directory.

        mode = "copy" - During output generation, the files are copied over from their original directories 
        mode = "cut"  - During output generation, the files are cut over from their original directories

        '''

        #First of all, let's do the work we need to do 
        path.mkdir(parents = True, exist_ok = True)        

        if node.name != "":

            if mode == "copy":
                print('copying ', node.name, 'to', path, self.variables[node.name])
                self.variables[node.name] = self.variables[node.name].copy(path)
                print('post copying ', node.name, 'to', path, self.variables[node.name])
            
            elif mode == "cut":
                print('cut', node.name, 'to', path, self.variables[node.name])
                self.variables[node.name] = self.variables[node.name].move(path)
                print('post cut', node.name, 'to', path, self.variables[node.name])
        
            
    def __post_generate(self, node, path = "", mode = "copy", flags = ""):
        '''
        Performs any post generation cleanup. For example, it handles the *d flag, which deletes anything
        irrelevant. We do this here to give a chance for any variable data to have been used / moved elsewhere.
        '''

        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory
        
        print('\n\n',new_path, node.flags)

        if node.flags == '*d' or node.flags == "*da" or flags == "*da":

            #We're going to make a list of all the files that should be there, and find all files that aren't in that list 
            print('On', new_path, node.is_root_dir())

            #First, we get a list of all children that aren't roots 
            children = [ (Path(new_path) / pth.directory) for pth in node.children if not pth.is_root_dir()]
            print('non root', children)

            #Then, we grab all the roots
            children += [ Path(pth.directory) for pth in node.children if pth.is_root_dir()]

            print('all', children)

            var_pths = []
            if node.name != '':
                #Next we grab all the values from our variables that are a part of the dir
                p = self.variables[node.name].filter(lambda x : new_path in x.parents)
                print(p)
                var_pths = p.vals()

            print('variable paths', var_pths)

            #Add 'em up, baby
            tot = children + var_pths
            print('Total', tot)

            bad_files = []
            for pth in Path(new_path).iterdir():
                if pth not in tot:
                    bad_files.append(pth)
                
            print('Bad files: ', bad_files)
            
            #Snip ... snip ... *ouch* >_<
            for fl in bad_files:
                print('Deleting', fl)
                if fl.is_dir():
                    shutil.rmtree(fl.as_posix())
                elif fl.is_file():
                    fl.unlink()
                else:
                    print('No clue how to handle this file')


        new_path = new_path.as_posix()

        for child in node.children:
            self.__post_generate(child, new_path, mode, "*da" if node.flags == "*da" else flags)
        

    def add_spec(self, spec_path):
        '''
        Adds a spec to parse
        '''

        #Construct an fgraph instance
        graph_to_add = self.__construct(spec_path)
        print(graph_to_add)
 
        #Verify the fgraph instance, and then add it in
        if self.__verify(graph_to_add):

            print('Verification successful.')
            self.file_graph.add_graph(graph_to_add)

            print('Graph added. Activating variables.')
            self.__activate(self.file_graph.fgraph_root)

            print('On standby. Variables: ')
            print(self.variables)
        else:
            print('Vertification failed. Maybe the spec has an invalid dir parameter specified somewhere?')

        print('Spec addition complete.\n\n')
    
    def create_spec(self, spec_path, mode = "cut", track = False):
        '''
        Creates a spec given by the spec path

        spec_path - filepath to the spec path
        mode - 
            - "cut": Any files that are being transferred to create this spec will be cut from their place
            - "copy": Any files that are being transferred to create this spec will be duplicated from their original place
        '''

        assert Path(spec_path).exists(), f"The spec to create at {spec_path} cannot be located"

        print('Creating spec.')

        #Construct the spec path
        graph_to_add = self.__construct(spec_path)

        print('Graph constructed. Activating variables.')

        #Do any actions inside the fgraph
        self.__output(graph_to_add, mode = mode)

        print('Output complete. Commencing cleanup.')

        #Do any cleanup inside the fgraph
        self.__post_generate(graph_to_add, mode = mode, flags = graph_to_add.flags)

        if track:
            print('Tracking requested. Adding to fgraph cluster.')

            self.file_graph.add_graph(graph_to_add)

            print('Graph added.')
            
    def get_vars(self):
        return self.variables
