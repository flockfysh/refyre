import argparse 
import sys
from refyre import Refyre
from refyre.core import RecipePreprocessor

#Instantiate an argument parser
def main(argv = None):
    parser = argparse.ArgumentParser(
        prog = "cli",
        description = "refyre v.0.0.1 CLI",
    )

    #Add positional arguments for input specs
    parser.add_argument("-i", '--input', help = "filepaths to the input specs, seperated by spaces", nargs='+')
    parser.add_argument("-o", '--output', help = "filepaths to the output specs, seperated by spaces", nargs='+')
    parser.add_argument("-r", '--recipe', help = "path to recipe / workflow file you want refyre to execute")

    #Add positional arguments for saving refyre state
    parser.add_argument("-s", '--save', help = "save the refyre state locally")

    args = parser.parse_args(argv)

    if args.recipe != None:
        RecipePreprocessor(args.recipe)

    ref = Refyre(input_specs = args.input, output_specs = args.output)

    if args.save:
        ref.save()

if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))