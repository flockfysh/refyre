# Refyre: Filesystem dominance is all you need
___ 

Refyre is an AI-fused Python package that provides two high level features:
- Easy large scale filesystem manipulations
- Efficient, code-less directory structuring and restructuring

Enhance your favorite Python packages such as Pandas, NumPy, Spark, and other data manipulation tools to quickly structure scattered data.

## Features
- Filesystem agnostic data handshakes 
- Kickstart loading entire repositories & setting up virtual environments in a single command, your way
- Perform mass operations on files such as copying, moving, zipping, POST-ing, in 1 line of code
- Homebrew structured data such as Pandas DataFrames, and image datasets in a snap of your fingers (< 30 lines)
- Refactor, organize, and analyze periodic research experiments with zero lines of code

## Quickstart
Simply provide refyre with an "input specification", telling it what directories to focus on

`sample_input_spec.txt`
```python
'''
Suppose you have a directory structure

a/
    a1.txt
    a2.txt
    ...
b/
    c/
        c1.txt
        c2.txt
        d.txt
        d2.txt
        ...

You seek to analyze the a files and the c files
'''
[dir="a"|name="a_var"]
[dir="b"]
    [dir="c"|pattern="gc?.txt"|name="c_var"] #Glob patterns start with 'g', regex with 'r', no need for just normal pattern matching
```

Have refyre analyze the directory with the following:
```python
#Main analysis line
ref = Refyre(input_specs = ['sample_input_spec.txt'])

#Now, have a bit of fun!
a_var = ref["a_var"]
c_var = ref["c_var"]

print(len(a_var)) #Number of files

#Move all the files to another directory, copy works the same way
a_var = a_var.move('dir2') #.copy() ...

#Get all the files in a List[Pathlib.Path] objects
all_a_var = a_var.vals()

#Automatically zip a copy of all the files 
zipped_c_var = c_var.zip()

print(len(zipped_c_var)) #1, the zipped c_var files

#Get all the parents dirs
c_var_parent_dirs = c_var.dirs()

print(type(c_var)) #refyre.fcluster.FileCluster (this is what each variable type is)

#Do mass file management operations such as delete(), filter()
all_a_var_and_c_vars = FileCluster(values = []) #Values are strings of filepaths you want to do operations on
all_a_var_and_c_vars = a_var + c_var

filtered_c = all_a_var_and_c_vars.filter(lambda p : p.name.startswith('c'))

#Delete all files
filtered_c.delete()

#Automatically account for any modifications by variables
print(len(all_a_var_and_c_vars))

```

And finally, after any analysis, you can use the variables to generate
specs

Let's say you want to generate directories & data in the format specified by `output_spec.txt`:

```python
'''
Sample output spec, creates
directories d & e, and ports the data
from a_var and c_var into it.
'''
[dir="d"|name="a_var"]
[dir="e"|name="c_var"]
```

One line.
```python
ref.create_spec('output_spec.txt')
```

Alternatively, this entire process (minus the in-between analysis) can be done through our CLI.
```python
refyre -i input.txt -o output.txt
```
