import re

'''
Utility methods for regex related things 
'''

def is_valid_regex(string):
    try:
        re.compile(string)
        return True
    except re.error:
        return False