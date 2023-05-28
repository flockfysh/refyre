refyre, an easy library to manipulate and transport data

## Contributing Conventions:

### Imports

If you wish to import from a file *in the same directory* , use a .

Here's a live example from `Parser.py`, where we import `Lexer.py`

```
from .Lexer import Lexer
```

If you need to import from a file *from **another** directory*, use refyre.

Here's a live example from `Parser.py`, where we import `FileGraphNode.py` to build our fgraph.

```
from refyre.fgraph import FileGraphNode
```