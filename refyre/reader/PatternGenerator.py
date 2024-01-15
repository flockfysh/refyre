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
    REGEX_STARTER = 'r!'
    GLOB_STARTER = 'g!'

    def is_valid_regex(pattern_string):
        logger.debug(pattern_string)
        if pattern_string.startswith(PatternGenerator.REGEX_STARTER):
            try:
                re.compile(pattern_string[2:])
            except re.error as e:
                logger.error(e)
                return False
        elif pattern_string.startswith(PatternGenerator.GLOB_STARTER):
            try:
                re.compile(fnmatch.translate(pattern_string[2:]))
            except re.error as e:
                logger.error(e)
                return False
        else:
            if not PatternGenerator.is_valid_genexp(pattern_string):
                logger.debug('not a valid')
                return False
        return True

    def is_valid_genexp(expression):
        return ExpressionGenerator.is_valid_genexp(expression)
    
    def convert_generator_expression(expression):
        return ExpressionGenerator.convert_generator_expression(expression)

    def get_pattern_type(pattern_string):
        if pattern_string.startswith(PatternGenerator.REGEX_STARTER):
            return "regex"

        if pattern_string.startswith(PatternGenerator.GLOB_STARTER):
            return "glob"
        
        #Handle generator expressions
        if not ExpressionGenerator.is_null_generator(pattern_string):
            logger.debug('here, we think it is a expgen')
            return "generator_expression"

        #Else, the string is a normal string
        return "normal_string" 

    def __new__(self, pattern_string, given_type = None):
        '''
            Takes in an input pattern string and returns the appropriate regex pattern.

        '''
        if given_type == 'regex' or given_type == 'r':
            return pattern_string

        if given_type == 'glob' or given_type == 'g':
            return fnmatch.translate(pattern_string)

        if given_type == 'expression_generator' or given_type == 'e':
            return ExpressionGenerator.convert_generator_expression(pattern_string)
        
        if given_type == 'normal' or given_type == 'n':
            return None 

        #If the type isn't given, we'll have to infer it
        if pattern_string.startswith(PatternGenerator.REGEX_STARTER):
            logger.debug('regex')
            return pattern_string[2:]

        if pattern_string.startswith(PatternGenerator.GLOB_STARTER):
            logger.debug('glob')
            return fnmatch.translate(pattern_string[2:])
        
        #Handle generator expressions
        if not ExpressionGenerator.is_null_generator(pattern_string):
            return ExpressionGenerator.convert_generator_expression(pattern_string)

        #Else, the string is a normal string
        return pattern_string