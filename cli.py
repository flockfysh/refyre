import argparse 
from refyre import Refyre

#Instantiate an argument parser
parser = argparse.ArgumentParser(
    prog = "cli",
    description = "refyre v.0.0.1 CLI",
)

#Add positional arguments for input specs
parser.add_argument("-i", '--input', help = "filepaths to the input specs, seperated by spaces", nargs='+')
parser.add_argument("-o", '--output', help = "filepaths to the output specs, seperated by spaces", nargs='+')

args = parser.parse_args()

ref = Refyre(input_specs = args.input, output_specs = args.output)