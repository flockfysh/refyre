#from refyre.core import RecipePreprocessor
from refyre import Refyre
from refyre.config import log

ref = Refyre(input_specs = ['i.txt'])

log("CREATING OUTPUT SPEC NOW")

ref.create_spec('o.txt', mode ="copy", track = True)

#print(ref["vars"])

for i in range(5):
    ref.step()

#print(ref.alias_manager)
