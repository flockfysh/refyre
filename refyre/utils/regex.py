import re
import fnmatch

'''
Utility methods for regex related things 
'''

def is_valid_regex(string):
    try:
        re.compile(fnmatch.translate(string))
        return True
    except re.error:
        return False