from refyre.fgraph import FileGraph
from refyre.reader import Lexer, Parser, ExpressionGenerator, VariableParser, PatternGenerator, VariableAction
from refyre.fcluster import FileCluster
from refyre.utils import is_valid_regex, clone_node, extract_numbers
from refyre.config import logfile, log
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

        #Initialize the fgraphs, proto and real

        #The proto 
        self.file_graph_blueprint = FileGraph() 
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


        log('HEEEERE', input_path)
        p = Parser(Lexer(input_path))

        log("CONSTRUCT", p)

        #Monkey patch, until we figure out how we can support directory clustering with output
        return p.copy(), self.__expand(p, path = expand_path)[0] 
        
    def __reconstruct(self, input_fgraph, expand_path = "", step = True):
        '''
            Reconstruct 
                - A mirror operation to the construct, except done with an
                fgraph as an input
        '''
        return input_fgraph.copy(), self.__expand(input_fgraph, path = expand_path, step = step)[0]


    def __expand(self, node, path = "", step = False):
        '''
            Expands all regex directories THAT EXIST into a static fgraph.

            If no such directories exist, we leave the node unaltered.

            This method enables a single cluster to target multiple directories
        '''
        if not node:
            return [None]

        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory

        assert Path(path).exists(), f"Error, the path {path} doesn't exist"
        log('new path: ', new_path, node.directory, node.pattern)
        
        if (Path(path).is_file()) or (not new_path.exists() and not PatternGenerator.is_valid_regex(node.directory)):
            log('invalid in general')
            return [None]
        

        #Handle limits 
        has_limit, lower, upper = False, 0, 1000000000
        if node.limit != '':
            has_limit = True
            lower, upper = extract_numbers(node.limit)
        log("LIMIT STUFF", lower, upper, has_limit)


        log("DIR ", node.directory, )
        t = PatternGenerator.get_pattern_type(node.directory)
        log('detected pattern to be ', t, node.directory == '', )

        if t != "normal_string":
            file_num = 0
            ret = []

            log(t, )

            if (t == "regex" or t == "glob") and node.directory != '':
                log('valid regex', )

                #Create nodes for each of the pattern matches
                log(new_path, new_path.parent, )
                for fl in new_path.parent.iterdir():

                    log('file', fl, )
                    log(r'{}'.format(node.directory), fl.as_posix(), )
                    if re.search(r'{}'.format(PatternGenerator(node.directory)), fl.as_posix()) and fl not in ret and fl.is_dir() and file_num >= lower and file_num <= upper: #No files will be allowed to be fclusters

                        pattern_matched_node = node.copy()
                        assert pattern_matched_node.pattern == node.pattern, f"Copy node has pattern {pattern_matched_node.pattern} while node has pattern {node.pattern}"

                        assert type(fl.name) == str
                        #Update the directory with the name 
                        pattern_matched_node.directory = fl.name 

                        log('found match', fl.name, )
                        file_num += 1
                        ret.append(pattern_matched_node)                 
            
            elif t == "generator_expression":

                #If the limit is specified, we create a node for every number within the range
                gen_func = ExpressionGenerator(node.directory)

                mx_num = -1

                log('\n\n\nGENERATOR!!!!', )

                if has_limit:
                    for j in range(lower, upper + 1):
                        new_node = node.copy()
                        new_node.directory = gen_func(j)
                        ret.append(new_node)
                    
                    mx_num = upper

                #If the limit isn't specified, we detect every node that follows the pattern                    
                else:
                    
                    for fl in new_path.parent.iterdir():

                        log("DIR", node.directory, )
                        reversed_num = ExpressionGenerator.reverse_generator_expression(node.directory, fl.name)
                        if reversed_num:
                            mx_num = max(mx_num, reversed_num)

                            pattern_matched_node = node.copy()
                            assert pattern_matched_node.pattern == node.pattern, f"Copy node has pattern {pattern_matched_node.pattern} while node has pattern {node.pattern}"

                            assert type(fl.name) == str
                            #Update the directory with the name 
                            pattern_matched_node.directory = fl.name 

                            log('found match', fl.name, )
                            file_num += 1
                            ret.append(pattern_matched_node)  

                log('\n\n\n', )
                log(step, '*s', node.flags, '*s' in node.flags, )
                if step and '*s' in node.flags:
                    new_node = node.copy()

                    log('adding new dir', mx_num + 1, )
                    new_node.directory = gen_func(mx_num + 1)


                    #Take a pause to generate the new directory 
                    self.__output(new_node, new_path.parent, mode = "copy")


                    ret.append(new_node)

            
            #Before we go to children, let's handle any imports we must
            log('handling imports', node.imports, node.directory, )
            import_fgraph = None
            if node.imports != '' and Path(node.imports).exists():
                log('importing', node.imports, )
                import_fgraph = self.__construct(node.imports, expand_path = new_path)
                import_fgraph.is_root = False
                log('imported', import_fgraph, )

            #Now, attempt to check for all the node children of the original node
            #We will insert each of the current node's children into the new matched nodes, and recurse on them

            for i, pattern_node in enumerate(ret):
                nchilds = []

                new_path = Path(pattern_node.directory) if pattern_node.is_root_dir() else Path(path) / pattern_node.directory 
                for child in node.children + [import_fgraph]:
                    nchilds.extend(self.__expand(child, new_path, step = step))

                pattern_node.children = [c for c in nchilds if c is not None] 

                if node.flags == '*m' and not new_path.exists():
                    log('making uncreated dir', )
                    new_path.mkdir(exist_ok = True, parents = True)

                if pattern_node.type == 'git' and pattern_node.link != '':
                    clone_node(pattern_node.link, new_path)

                if pattern_node.alias != '':
                    log('adding', pattern_node.alias, )

                    log('reversing', node.directory, pattern_node.directory, )
                    n = ExpressionGenerator.reverse_generator_expression(node.directory, pattern_node.directory)

                    if ( ('*s' in node.flags or '*l' in node.flags) and n == mx_num + 1):
                        self.alias_manager.add( ExpressionGenerator(pattern_node.alias)(1), Path(new_path.as_posix()), is_pathlib = True)
                    elif not ('*s' in node.flags or '*l' in node.flags):
                        self.alias_manager.add( ExpressionGenerator(pattern_node.alias)(n), Path(new_path.as_posix()), is_pathlib = True)
                    

            return ret if ret else [node]

        else:
            log('in else', )
            #Before we go to children, let's handle any imports we must
            log('handling imports', node.imports, node.directory, )
            import_fgraph = None
            if node.imports != '' and Path(node.imports).exists():
                log('importing', node.imports, )
                
                import_fgraph = self.__construct(node.imports, is_output = True)
                import_fgraph.is_root = False

                log("EEEEEETKJSDLKJSADL", )
            
            if node.flags == '*m' and not new_path.exists():
                new_path.mkdir(exist_ok = True, parents = True)

            if node.type == 'git' and node.link != '':
                clone_node(node.link, new_path)
                
            if node.alias != '':
                log('adding', node.alias, )
                log(ExpressionGenerator(node.alias)(1), )
                self.alias_manager.add(ExpressionGenerator(node.alias)(1), Path(new_path.as_posix()), is_pathlib = True)

            nchild = []
            for child in node.children + [import_fgraph]:
                nchild.extend(self.__expand(child, new_path, step = step))
            
            node.children = [c for c in nchild  if c is not None]

            return [node]

    def __verify(self, node, path = ""):
        '''
            A simple verification method to ensure the basic integrity of a fgraph.

            This method ONLY CHECKS TO SEE IF DIRECTORIES ARE LEGIT. It does nada mas.

            Assumptions:
                - If a node is root, it will be the base directory, and the absolute path will be taken from there.
        '''
        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory

        log('Testing to see if ', new_path, 'exists', )
        if not new_path.exists():
            return [False, None]
        
        new_path = new_path.as_posix()

        if not node.children:
            return [True, node]

        ret = []
        for child in node.children:
            ret.append(self.__verify(child, new_path))


        node.children = [out[1] for out in ret if out[1] != None]

        return [any([out[0] for out in ret]), node]
    

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
            log('activating', new_path, node.directory, node.name, )
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

        log('mode', node.mode, )
        self.__create_output(node, new_path, mode if node.mode == '' else node.mode)
        new_path = new_path.as_posix()

        for child in node.children:
            self.__output(child, new_path, "copy")
        

    def __clear(self, wipe_proto = True, wipe_vars = True):
        '''
            Wipes the refyre instance clean.
        '''

        if wipe_vars:
            self.variables.clear()
        self.alias_manager.clear()
        self.code_manager.clear()

        self.file_graph = FileGraph()

        if wipe_proto:
            self.file_graph_blueprint = FileGraph()

        gc.collect()

    def __parse_var(self, node, path, mode):
        '''
        Parses all the options in the "names" attribute.

        I expect this method to blow up as this codebase grows (it's an options methods, and you never can have enough options!), 
        so once this goes over 100 lines, we'll move
        it into the fgraph directory.
        '''

        if mode == "normal":
            name, v = VariableAction(node.name, node, path, self.variables, self.out_temp_var_dict,  True, False, mode = mode)
            log('updated vals', name, v, )

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
            name, v = VariableAction(node.name, node, path, self.variables, self.out_temp_var_dict , False, True, mode = mode)
            log('updated vals', name, v, )

            
    def __post_generate(self, node, path = "", mode = "copy", flags = ""):
        '''
        Performs any post generation cleanup. For example, it handles the *d flag, which deletes anything
        irrelevant. We do this here to give a chance for any variable data to have been used / moved elsewhere.
        '''

        new_path = Path(node.directory) if node.is_root_dir() else Path(path) / node.directory
        
        log('\n\n',new_path, node.flags, )

        if node.flags == '*d' or node.flags == "*da" or flags == "*da":

            #We're going to make a list of all the files that should be there, and find all files that aren't in that list 
            log('On', new_path, node.is_root_dir(), )

            #First, we get a list of all children that aren't roots 
            children = [ (Path(new_path) / pth.directory) for pth in node.children if not pth.is_root_dir()]
            log('non root', children, )

            #Then, we grab all the roots
            children += [ Path(pth.directory) for pth in node.children if pth.is_root_dir()]

            log('all', children, )

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


                log(p, )
                var_pths = p.vals()

            log('variable paths', var_pths, )

            #Add 'em up, baby
            tot = children + var_pths
            log('Total', tot, )

            bad_files = []
            for pth in Path(new_path).iterdir():
                if pth not in tot:
                    bad_files.append(pth)
                
            log('Bad files: ', bad_files, )
            
            #Snip ... snip ... *ouch* >_<
            for fl in bad_files:
                log('Deleting', fl, )
                if fl.is_dir():
                    shutil.rmtree(fl.as_posix())
                elif fl.is_file():
                    fl.unlink()
                else:
                    log('No clue how to handle this file', )


        new_path = new_path.as_posix()

        for child in node.children:
            self.__post_generate(child, new_path, mode, "*da" if node.flags == "*da" else flags)
        

    def add_spec(self, spec_path):
        '''
        Adds a spec to parse
        '''

        #Construct an fgraph instance
        proto, graph_to_add = self.__construct(spec_path, is_output = False)
        log(graph_to_add, )
 
        #Verify the fgraph instance, and then add it in
        verification_successful, verified_graph = self.__verify(graph_to_add)
        if verification_successful:

            log('Verification successful.', )
            log(verified_graph, )
            log()

            self.file_graph_blueprint.add_graph(proto)
            self.file_graph.add_graph(verified_graph)

            log('Graph added. Activating variables.\n\n', )
            log(self.file_graph, )
            log('\n\n', )

            self.out_temp_var_dict = self.variables.copy()

            self.__activate(self.file_graph.fgraph_root)

            self.variables = self.out_temp_var_dict

            log('On standby. Variables: ', )
            log(self.variables, )
        else:
            log('Vertification failed. Maybe the spec has an invalid dir parameter specified somewhere?', )

        log('Spec addition complete.\n\n', )
    
    def create_spec(self, spec_path, mode = "cut", track = False):
        '''
        Creates a spec given by the spec path

        spec_path - filepath to the spec path
        mode - 
            - "cut": Any files that are being transferred to create this spec will be cut from their place
            - "copy": Any files that are being transferred to create this spec will be duplicated from their original place
        '''

        assert Path(spec_path).exists(), f"The spec to create at {spec_path} cannot be located"

        log('Creating spec.', )

        #Construct the spec path
        proto, graph_to_add = self.__construct(spec_path)

        log(graph_to_add, )
        log('Graph constructed. Activating variables.', )

        self.out_temp_var_dict = self.variables.copy()

        #Do any actions inside the fgraph
        self.__output(graph_to_add, mode = mode)

        self.variables = self.out_temp_var_dict

        log('Output complete. Commencing cleanup.', )

        #Do any cleanup inside the fgraph
        self.__post_generate(graph_to_add, mode = mode, flags = graph_to_add.flags)

        if track:
            log('Tracking requested. Adding to fgraph cluster.', )

            self.file_graph_blueprint.add_graph(proto)
            self.file_graph.add_graph(graph_to_add)

            log('Graph added.', )
            
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
    
    def aliases(self):
        return self.alias_manager

    def step(self):
        '''
        Reconstructs all the variables, generates / functions towards all 
        directories with a '*s' flag in the following ways, based on the flags below:
        
            '*wl' - base write, write latest cluster in the pattern sequence

        Updates to arch - 
        
        Need to maintain a "blueprint" fgraph, pre expansion AND current fgraph

        During step, each directory is created / analyzed
        '''

        log('\n\n\n STEPPPY', )

        #Prevent conflicts
        self.out_temp_var_dict = self.variables.copy()

        self.__clear(wipe_proto = False)

        self.variables = self.out_temp_var_dict.copy()

        #Reset the state
        self.file_graph_blueprint.fgraph_root, renewed_fgraph = self.__reconstruct(self.file_graph_blueprint.fgraph_root)
        self.variables = self.out_temp_var_dict

        #Add and activate the fgraphs
        self.file_graph.add_graph(renewed_fgraph)


        log('Step complete', )
