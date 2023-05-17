#Use this file for general tests
from refyre import Refyre

ref = Refyre()
ref.add_spec('tests/spec_tests/level1/casual_refactor/input.txt')

ref.add_spec('tests/spec_tests/level1/casual_refactor/input.txt')

print(ref.file_graph)