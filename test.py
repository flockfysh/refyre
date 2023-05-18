#Use this file for general tests
from refyre import Refyre

ref = Refyre()
ref.add_spec('inp.txt')

zipped = ref["var1"].zip()