# Core Features

Let's provide a quick overview of the basic capabilities refyre packs.

### Spec Attributes:

Specs, as shown above are a Pythonic way for you to feed information to refyre. Each [] represents a *cluster*, which usually has a dir attribute specified. Attributes are seperated using the '|' seperator. 

As shown above, Pythonic comments can be used in a similar fashion to Python. Back to the various attributes:

- **dir**: Specifies the directory the cluster is targeting. *Usually, the clusters are relative paths*.
    - You can specify the three pattern types to target multiple directories
- **pattern**: Allows you to target specific files by specifying a template pattern. Currently, glob, regex, and "generator expressions" are supported.
  - For glob patterns, add a 'g!' before the pattern; ex: `g!*.txt`
  - For regex patterns, add an 'r!' before the pattern ex: `r!.txt`
  - Generator expressions a simplified pattern matching, that's more humanly controllable
    - Just one template matching --> `$` matches to a number
    - refyre supports generator expressions the most out of the three

- **name**: The workhorse of specs. Arguably the **meat** of the spec. Assigns all the values to a variable specified by **name**. *Only single variable / cluster are supported*
    - You can achieve 'appending' by specifying a `+` before the name
- **flags**: A grab bag of various tricks you can use. You can specify as many as you want, and they work together to bring out cool cluster behaviours
  - `*m` makes a directory if it doesn't exist in a read spec
  - `*d` (only during generation) deletes everything in the *current* directory except for the clusters specified
  - `*da` deletes everything in the *current & all subclusters* except for clusters listed
  - `*f` gets all the files listed in the current directory
  - `*d` gets all the directories listed in the current directory
  - `*r` allows `*f` and `*d` to behave recursively (i.e, get all files from subdirectories, etc.)
  - `*s` enables *step generation*, Each time `refyre.step()` is called, the next directory in the pattern is generated. (ex:, if `dir="test$"` and `*s`, `test1` would be generated on first `.step()`, `test2`, ...)
  - `*c` enables code analysis. If you seek to import a directory / repository you recently cloned, you can specify the `*c` flag and then import it in your code
  - `type & link` are used for specific behaviours, most commonly *git cloning*. Automatically clone in repos by specifying `type="git"` and the link to your git.
- **mode**: Can either be set to `cut` or `copy`. During generation, the variable files will either be cut or copied to their respective place.
- **limit**: Limits the number of results targeted, or directories generated
- **serialize** specify a generator expression to rename all the files into a consistent format

These are all the basic quantifiers you can use, they cover ~80% of refyre's inner power. The other 20% are pretty obscure and aren't that useful normally.

### FileClusters (Variables)

Variables are the backbone of refyre. The clusters provide an *avenue* for the variables to easily target the data without worrying about writing any code. However, they aren't the only way to access variable's powers. The docs below, again, specify the most useful abilities for these variables.

`FileCluster(values = [], dirs = [], patterns = [], as_pathlib = False,)`
    - `values`: string filepaths, or `Path` objects depending on whether `as_pathlib` is true or false.
    - `patterns`: corresponds to the dirs, lists what patterns you want to target

FileClusters are strongly rooted in *object oriented operations*, meaning each operation returns another FileCluster, so you can continue channeling FileCluster capabilities. To get out of FileClusters, you can use the following options:
    - `.vals()`: Returns a list of Path objects
    - `.item()`: Returns the first Path object

Using this basic constructor, you can make some easy operations:
  - `.move(target_dir)`
  - `.copy(target_dir)`
  - `.filter(filter_func)`
  - `.map(map_func)`
  - `.zip()`
  - `.delete()`
  - `.post(url, additional_data, payload_name)` 
  - `.filesize()`
  - `.clone()`

You can also do other operations between FileClusters
  - `+` (Returns the sum of the contents of two FileClusters)  
  - `-` (Returns the contents in the current FileCluster while removing all other contents that are also in the other FileCluster)
  - `&` (Intersection operator)
  - `|` (Union operator)

### The Refyre Object

These docs are running too long already, I will try to keep this as short as possible.

- `Refyre(input_specs = [], output_specs = [])`
  - Instantiates a refyre spec

- `add_spec(spec_path, track = False)`
  - Adds a spec for refyre *reading*. If track is set to true, it can
  later be reused for step generation.

- `create_spec(spec_path, track = False)`
  - Creates a spec. If track is set to true, it can later be reused for step 
  generation.

- `step()`
  - Any specs with a `*s` attribute have the next directory in the patterns they specify generated

Accessing variables can be done using the `[]` notation. Use it to get and attach variables to a `Refyre` object.

**Congratulations, you know everything to be a refyre expert!**

### Misc Docs

#### DataStack
Let's say you want to brew a dataset & structure data of you're own. refyre allows you to combine the power of variables with the DataStack, processing them to create constructs such as Pandas Dataframes.

The process is twofold - (1) *secure your variables*, and then (2) *run them through the DataStack*. The DataStack itself is a *processor*, taking in a bunch of variables, and producing the variables.

Your job with the DataStack will be to figure out how can you convert the variables to the dataset format you want.

Consider the PandasStack (a DataStack). Here, your job is to figure out how you can convert each row of variables into a *DataFrame column*

```python

from refyre import Refyre
from refyre.datastack import PandasStack
from PIL import Image
import pandas as pd

ref = Refyre(input_specs = ['specs/in.txt'])

#We will do some pandas visualizations on the input data
stack = PandasStack(AssociationCluster(input_vars = [ref["images"]]))

def processor(fp):
    print('processing', fp)
    im = Image.open(fp).convert('RGB')
    width, height = im.size 

    ar, ag, ab = 0.0, 0.0, 0.0
    for i in range(width):
        for j in range(height):
            r, g, b = im.getpixel((i, j))
            ar, ag, ab = ar + r, ag + g, ab + b 
        
    ar, ag, ab = ar / (width * height), ag / (width * height), ab / (width * height)
    return (fp.name, width, height, ar, ag, ab)

df = stack.create_dataframe(['image_name', 'image_width', 'image_height', 'average_red', 'average_green', 'average_blue'], processor)
```

As you can see, the majority of the work here comes from building a *processor* method to convert each row of variables into a DataFrame row.
