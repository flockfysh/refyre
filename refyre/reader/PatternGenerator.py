import fnmatch
import re

class PatternGenerator:
    '''
        The pattern generator is designed to parse all pattern based 
        strings and return regex versions of them that can be used to 
        pattern match.

        We created the generator to help differentiate between glob patterns and
        regex. Most of the time, people use glob, but sometimes the power of regex 
        matching does come in handy. 

        A glob string will come in the normal form. A regex string will start with an r before the actual pattern.

        ex: "a?.txt" is a glob pattern. "ra?.txt" is regex.

    '''
    def is_valid_regex(pattern_string):
        if pattern_string.startswith('r'):
            try:
                re.compile(pattern_string[1:])
            except re.error:
                return False
        else:
            try:
                re.compile(fnmatch.translate(pattern_string))
            except re.error:
                return False

        return True

    def __new__(self, pattern_string):
        '''
            Takes in an input pattern string and returns the appropriate regex pattern.

        '''
        if pattern_string.startswith('r'):
            print('regex')
            return pattern_string[1:]

        #Clear out any leading / trailing spaces 
        print('glob')
        return '' if pattern_string == '' else fnmatch.translate(pattern_string.strip())