from .Lexer import Lexer
from .cogs.LexerToken import Token

from refyre.fgraph import FileGraphNode
from pathlib import Path


#Utility stack (LIFO) data stucture methods
def push(stack, item):
    stack.append(item)

def pop(stack):
    return stack.pop()

class Parser:
    '''
        Refyre's static parser
    '''
    def parse(tokens, INF = -10, ):
        '''
        Things to note: 
            - Floor for tab depth is set to be -10. If it goes beyond this, ...
            the circus would really love to hire their new rising clown.
        '''
        stack = []

        #Push our virtual top
        push(stack, (FileGraphNode(is_root = True, children = []), INF))

        
        for tok in tokens:
            cur = []

            #Resolve all the nodes with tab_level lower
            while tok.tab_level < stack[-1][1]:
                top = pop(stack)

                #Grab all the nodes with the same level
                while stack[-1][1] == top[1]:
                    p = pop(stack)[0]
                    cur = [p] + cur 

                #Append top last to preserve ordering - THIS IS CRUCIAL TO PRESERVE USER INTENT
                cur.append(top[0])
                
                #Now, we know that the next node, whatever it is, must have a lower level
                stack[-1][0].add_children(cur)

                #Clear the list
                cur.clear()

            print('imports', tok.imports, tok.link)
            push(stack, (FileGraphNode(children = list([]), pattern = tok.pattern, directory = tok.directory, type = tok.dirtype, name = tok.name, is_root = Path(tok.directory).exists(), flags = tok.flags, serialize = tok.serialize, imports = tok.imports, mode = tok.mode, link = tok.link, alias = tok.alias) , tok.tab_level))

        #Compress the remainder of the stack
        while len(stack) > 1: 

            top = pop(stack)
            cur = []

            while top[1] == stack[-1][1]:
                #Grab all the nodes with the same level
                p = pop(stack)[0]
                cur = [p] + cur
            
            #Append top last to preserve ordering - THIS IS CRUCIAL TO PRESERVE USER INTENT
            cur.append(top[0])

            #Now, we know that the next node, whatever it is, must have a lower level
            stack[-1][0].add_children(cur)

            #Clear the list
            cur.clear()
        
        assert len(stack) == 1 and stack[0][1] == INF, "Improper root node, something went wrong in the parsing algorithm"
        

        return stack[0][0]

    def __new__(self, tokens):
        assert type(tokens) == list and all([type(t) == Token for t in tokens]), "Invalid type found from Lexer output; something's going wrong."
        return Parser.parse(tokens)