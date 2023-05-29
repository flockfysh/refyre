from refyre.fgraph import FileGraph
from refyre.reader import Lexer, Parser, ExpressionGenerator, VariableParser, PatternGenerator
from refyre.fcluster import FileCluster
from refyre.utils import is_valid_regex, clone_node
from refyre.core import CodeManager, AliasManager

#pathlib
from pathlib import Path

#Garbage collection
import gc

#Regex
import re

#Deleting
import shutil

#Globbing
import fnmatch

#json 
import json

class Refyre:

    def __init__(self, input_specs = None, output_specs = None, variables = None):
        '''
            input_specs: A List[Str] of filepaths to the various specs refyre will target
        '''

        self.variables = {} if not variables else variables
        self.file_graph = FileGraph()
        self.code_manager = CodeManager()
        self.alias_manager = AliasManager()

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
        return self.variables[key] if key in self.variables else None
    

    #The Five Fundamental Operations of Refyre
    def __construct(self, input_path, is_output = False, expand_path = ""):
        '''
            Construct Operation:
                - Receives an input spec, and creates an fgraph
        '''


        print('HEEEERE', input_path)
        p = Parser(Lexer(input_path))

        #Monkey patch, until we figure out how we can support directory clustering with output
        return self.__expand(p, path = expand_path)[0] if not is_output else p
    


    def __expand(self, node, path = "", need_to_append = False):
        '''
            Expands all regex directories into a static fgraph.

            This method enables a single cluster to target multiple directories
        '''
        if not node:
            return [None]

        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory
        assert Path(path).exists(), f"Error, the path {path} doesn't exist"
        print('new path: ', new_path, node.directory, node.pattern)
        
        if (Path(path).is_file()) or (not new_path.exists() and not PatternGenerator.is_valid_regex(node.directory)):
            print('invalid in general')
            return [None]
        
        #If we are in some sort of sub directory, all variable operations must be appends by default
        print("NEED_TO_APPEND", need_to_append)
        if need_to_append and node.name != '' and not node.name.startswith('+'):
            node.name = '+' + node.name

        if not new_path.exists() and PatternGenerator.is_valid_regex(node.directory) and node.directory != '':
            print('valid regex')

            #Create nodes for each of the pattern matches
            ret = []
            print(new_path, new_path.parent)
            for fl in new_path.parent.iterdir():

                print('file', fl)
                print(r'{}'.format(node.directory), fl.as_posix())
                if re.search(r'{}'.format(PatternGenerator(node.directory)), fl.as_posix()) and fl not in ret and fl.is_dir(): #No files will be allowed to be fclusters

                    #Ensure the node name has append mode, so that all the data across gets added
                    if node.name != '' and not node.name.startswith('+'):
                        node.name = '+' + node.name


                    pattern_matched_node = node.copy()
                    assert pattern_matched_node.pattern == node.pattern, f"Copy node has pattern {pattern_matched_node.pattern} while node has pattern {node.pattern}"

                    assert type(fl.name) == str
                    #Update the directory with the name 
                    pattern_matched_node.directory = fl.name 
                    need_to_append = True

                    print('found match', fl.name, need_to_append)

                    ret.append(pattern_matched_node)                 
            
            #Before we go to children, let's handle any imports we must
            print('handling imports', node.imports, node.directory)
            import_fgraph = None
            if node.imports != '' and Path(node.imports).exists():
                print('importing', node.imports)
                import_fgraph = self.__construct(node.imports, expand_path = new_path)
                import_fgraph.is_root = False
                print('imported', import_fgraph)

            #Now, attempt to check for all the node children of the original node
            #We will insert each of the current node's children into the new matched nodes, and recurse on them

            for i, pattern_node in enumerate(ret):
                nchilds = []

                new_path = Path(pattern_node.directory) if pattern_node.is_root_dir() else Path(path) / pattern_node.directory 
                for child in node.children + [import_fgraph]:
                    nchilds.extend(self.__expand(child, new_path, need_to_append = need_to_append))

                pattern_node.children = [c for c in nchilds if c is not None] 

                if node.flags == '*m' and not new_path.exists():
                    print('making uncreated dir')
                    new_path.mkdir(exist_ok = True, parents = True)

                if pattern_node.type == 'git' and pattern_node.link != '':
                    clone_node(pattern_node.link, new_path)

                if pattern_node.alias != '':
                    print('adding', pattern_node.alias)

                    self.alias_manager.add( ExpressionGenerator(pattern_node.alias)(i), Path(new_path.as_posix()), is_pathlib = True)
                    

            
            return ret

        else:
            print('in else')
            #Before we go to children, let's handle any imports we must
            print('handling imports', node.imports, node.directory)
            import_fgraph = None
            if node.imports != '' and Path(node.imports).exists():
                print('importing', node.imports)
                
                import_fgraph = self.__construct(node.imports, is_output = True, need_to_append = need_to_append)
                import_fgraph.is_root = False

                print("EEEEEETKJSDLKJSADL")
            
            nchild = []
            for child in node.children + [import_fgraph]:
                nchild.extend(self.__expand(child, new_path))
            
            node.children = [c for c in nchild  if c is not None]

            if node.flags == '*m' and not new_path.exists():
                new_path.mkdir(exist_ok = True, parents = True)

            if node.type == 'git' and node.link != '':
                clone_node(node.link, new_path)
                
            if node.alias != '':
                print('adding', node.alias)
                print(ExpressionGenerator(node.alias)(1))
                self.alias_manager.add(ExpressionGenerator(node.alias)(1), Path(new_path.as_posix()), is_pathlib = True)

            return [node]

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
            print('activating', new_path, node.directory, node.name)
            self.__parse_var(node, new_path, mode)

        if node.flags != '':
            #Activate the code manager
            if '*c' in node.flags:
                self.code_manager.add(new_path)


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

        print('mode', node.mode)
        self.__create_output(node, new_path, mode if node.mode == '' else node.mode)
        new_path = new_path.as_posix()

        for child in node.children:
            self.__output(child, new_path, "copy")
        

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
                print(name, 'define', path)
                print('node', node)
                self.variables[name] = FileCluster(input_paths = [path], input_patterns = [node.pattern], recursive = "*r" in node.flags)

                print('\nactivation init', operator, node.pattern, path, 'var name', name)
                print('result: ', self.variables[name])

            elif operator == "+":
                self.variables[name] += FileCluster(input_paths = [path], input_patterns = [node.pattern], recursive = "*r" in node.flags)
                print('\nactivation append', operator, node.pattern, path, 'var name', name)
                print('result: ', self.variables[name])


            #Handle any flags 

            #*f flag - only keep the files 
            if '*f' in node.flags:
                self.variables[name] = self.variables[name].filter(lambda x : x.is_file())

            #*f flag - only keep directories
            if '*d' in node.flags:
                self.variables[name] = self.variables[name].filter(lambda x : x.is_dir())

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
            
            #Extract the key information
            print('extract', node.name)
            name, sliced, start, stop, step = VariableParser(node.name, self.variables)

            #The refresher method will eliminate the invalid paths, so let's add back in the new paths at their original positions
            v = self.variables[name].vals()

            if mode == "copy":
                print('copying ', name, 'to', path, sliced)
                sliced = sliced.copy(path)
                print('post copying ', name, 'to', path, sliced)
            
            elif mode == "cut":
                print('cut', name, 'to', path, sliced)
                sliced = sliced.move(path)
                print('post cut', name, 'to', path, sliced)
            

            s_v = sliced.vals()
            print(sliced, v, start, stop, step)
            for ind_s, ind_v in enumerate(range(start, stop, step)):
                print(ind_s, ind_v, s_v, v)
                v[ind_v] = s_v[ind_s]
            
            print('updated vals', v)
            self.variables[name] = FileCluster(values = v, as_pathlib = True)
            print(self.variables[name])

            
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
                #Extract the key information - handling slicing
                name, sliced = VariableParser(node.name, self.variables)

                #If we need to serialize the node, we do it first
                if node.serialize != '':
                    sliced = sliced.rename(ExpressionGenerator(node.serialize))
                    self.variables[name] += sliced

                #Next we grab all the values from our variables that are a part of the dir
                p = sliced.filter(lambda x : new_path in x.parents)


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
        graph_to_add = self.__construct(spec_path, is_output = False)
        print(graph_to_add)
 
        #Verify the fgraph instance, and then add it in
        if self.__verify(graph_to_add):

            print('Verification successful.')
            self.file_graph.add_graph(graph_to_add)

            print('Graph added. Activating variables.\n\n')
            print(self.file_graph)
            print('\n\n')

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
        graph_to_add = self.__construct(spec_path, is_output = True)

        print(graph_to_add)
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

    def save(self, save_dir = '.'):

        pths = {}

        for var_name in self.variables:
            pths[var_name] = []

            for p in self.variables[var_name]:
                pths[var_name].append(p.as_posix())
            
        save_pth = Path(save_dir) / "refyre_state.json"
        with open(save_pth.as_posix(), 'w') as f:
            json.dump(pths, f, indent = 4)
    
    def load(load_filename):

        with open(load_filename, 'r') as f:
            pths = json.load(f)

            variables = {}

            for name in pths:
                variables[name] = FileCluster(values = pths[name], as_pathlib = False)

            return Refyre(variables = variables)

