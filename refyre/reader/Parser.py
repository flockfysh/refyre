from .Lexer import Lexer
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
                cur.append(top[0])
                while stack[-1][1] == top[1]:
                    cur.append(pop(stack)[0]) 
                
                #Now, we know that the next node, whatever it is, must have a lower level
                stack[-1][0].add_children(cur)

                #Clear the list
                cur.clear()

            push(stack, (FileGraphNode(children = list([]), pattern = tok.pattern, directory = tok.directory, type = tok.dirtype, name = tok.name, is_root = Path(tok.directory).exists()) , tok.tab_level))

        #Compress the remainder of the stack
        while len(stack) > 1: 

            top = pop(stack)
            cur = [top[0]]

            while top[1] == stack[-1][1]:
                #Grab all the nodes with the same level
                cur.append(pop(stack)[0]) 
                
            #Now, we know that the next node, whatever it is, must have a lower level
            stack[-1][0].add_children(cur)

            #Clear the list
            cur.clear()
        
        assert len(stack) == 1 and stack[0][1] == INF, "Improper root node, something went wrong in the parsing algorithm"
        return stack[0][0]
