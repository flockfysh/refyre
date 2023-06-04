#Simple test designed to make sure that pytest is working properly

def test_always_passes():
    assert True

def test_imports():
    #fgraph
    from refyre.fgraph import FileGraph
    from refyre.fgraph import FileGraphNode

    #fcluster

    #datastack

    #reader
    from refyre.reader import Lexer
    from refyre.reader import Parser