import re 
from refyre.config import logger


class ExpressionGenerator:
    '''
        The ExpressionGenerator class takes in an 
        input generator string, such as test$.txt, and returns a
        lambda function that can be used to evaluate the expressions at various points.

        For example, test$.txt returns a lambda function, that when called at i = 1, returns test1.txt

        This class is a static class; it's sole purpose is to create an organized location
        to generate complex expressions.

        For now, only numbers are supported. You can generate number expressions using the '$' symbol 
        as shown above.

    '''
    def generate_expression(string):
        # Replace '$' with '{}' to use it as a placeholder for string formatting
        lambda_function = lambda i: string.replace('$', str(i))

        return lambda_function
    
    def is_valid_genexp(expression):
        pattern = r'^[a-zA-Z0-9/\-_$]+$'
        logger.debug(f'Pattern: {pattern}')
        logger.debug(f'Ret: {bool(re.match(pattern, expression))}')
        return bool(re.match(pattern, expression))
    
    def is_null_generator(expression):
        '''
            By "null" generator, I just mean a genexp that 
            doesn't have any special characters, i.e. one that will stay the same
        '''
        logger.debug(f"Checking: , {expression}, {'$' in expression}")
        return not ('$' in expression)
    
    def convert_generator_expression(expression):
        escaped_expression = re.escape(expression)
        regex_pattern = escaped_expression.replace(r'\$', r'(\d+)')
        return regex_pattern
    
    def reverse_generator_expression(expression, string):
        regex_pattern = ExpressionGenerator.convert_generator_expression(expression)

        logger.debug(f'{expression}, {regex_pattern}')
        match = re.match(regex_pattern, string)
        if match:
            logger.debug(f"{match.group(1)}, exp,  {expression}, str, {string}")
            return int(match.group(1))
        else:
            return None
        
    def __new__(self, string):
        '''
            Hijack the '__new__' method (usually used in constructors) 
            and make it do our bidding >:)

            Takes in an expression, return a lambda function.
        '''

        return ExpressionGenerator.generate_expression(string)