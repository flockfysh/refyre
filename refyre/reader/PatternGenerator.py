import fnmatch
import re
from .ExpressionGenerator import ExpressionGenerator
from refyre.config import logger

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
        logger.debug(pattern_string)
        if pattern_string.startswith('r'):
            try:
                re.compile(pattern_string[1:])
            except re.error as e:
                logger.error(e)
                return False
        elif pattern_string.startswith('g'):
            try:
                re.compile(fnmatch.translate(pattern_string[1:]))
            except re.error as e:
                logger.error(e)
                return False
        else:
            if not PatternGenerator.is_valid_genexp(pattern_string):
                return False
        return True

    def is_valid_genexp(expression):
        return ExpressionGenerator.is_valid_genexp(expression)
    
    def convert_generator_expression(expression):
        return ExpressionGenerator.convert_generator_expression(expression)

    def get_pattern_type(pattern_string):
        if pattern_string.startswith('r'):
            return "regex"

        if pattern_string.startswith('g'):
            return "glob"
        
        #Handle generator expressions
        if not ExpressionGenerator.is_null_generator(pattern_string):
            return "generator_expression"

        #Else, the string is a normal string
        return "normal_string" 

    def __new__(self, pattern_string):
        '''
            Takes in an input pattern string and returns the appropriate regex pattern.

        '''
        if pattern_string.startswith('r'):
            logger.debug('regex')
            return pattern_string[1:]

        if pattern_string.startswith('g'):
            logger.debug('glob')
            return fnmatch.translate(pattern_string[1:])
        
        #Handle generator expressions
        if not ExpressionGenerator.is_null_generator(pattern_string):
            return ExpressionGenerator.convert_generator_expression(pattern_string)

        #Else, the string is a normal string
        return pattern_string