#Use this file for general tests
from refyre import Refyre

ref = Refyre()
ref.add_spec('inp.txt')

ref.create_spec('oup.txt')