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

def get_optimal_pattern(string):
    try:
        log('string is a regex', string )
        re.compile(string)
        return string
    except re.error:
        return False
    
    try:
        log('string is a glob', string )
        re.compile(fnmatch.translate(string))
        return fnmatch.translate(string)
    except re.error:    
        return None

def extract_numbers(string):
    pattern = r'(\d+)(?:-(\d+))?$'
    match = re.match(pattern, string)
    if match:

        if not match.group(2):
            return 0, int(match.group(1))

        start = int(match.group(1))
        end = int(match.group(2))

        return start, end
    else:
        return None