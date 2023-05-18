from .FileGraphNode import FileGraphNode

class FileGraph:
    '''
        This class is really just a wrapper class.

        The goal is to provide a proxy interface for the Refyre objects to 
        interact with the fgraph without interfering with the inner
        workings.
    '''

    def __init__(self):
        #Make a virtual node stringing together all the graphs 

        #DO NOT DELETE THE children []. This led me on a 2 hour goose chase; i.e. object memory gets repeatedly screwed up, causing it to conflate values with another node. Don't delete it. DONT!!!
        self.fgraph_root = FileGraphNode(is_root = True, children = [])     


    def add_graph(self, graph):
        self.fgraph_root.add_child(graph)
    
    def __repr__(self):
        return repr(self.fgraph_root)
    
