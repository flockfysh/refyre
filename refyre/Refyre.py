from refyre.fgraph import FileGraph
from refyre.reader import Lexer
from refyre.reader import Parser

class Refyre:

    def __init__(self, input_specs = None):
        '''
            input_specs: A List[Str] of filepaths to the various specs refyre will target
        '''

        self.variables = {}
        self.file_graph = FileGraph()

        if input_specs:
            assert isinstance(input_specs, list)
            for spec in input_specs:
                self.add_spec(spec)

    def __getitem__(self, key):
        '''
            The refyre variables ("FileClusters") can be
            internally referred to through the Refyre object
        '''
        return self.variables[key]

    def add_spec(self, spec_path):
        p = Parser.parse(Lexer.lex(spec_path))
        self.file_graph.add_graph(p)
        

    def get_vars(self):
        return self.variables
