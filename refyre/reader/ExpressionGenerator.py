import re 





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

    def __new__(self, string):
        '''
            Hijack the '__new__' method (usually used in constructors) 
            and make it do our bidding >:)

            Takes in an expression, return a lambda function.
        '''

        return ExpressionGenerator.generate_expression(string)