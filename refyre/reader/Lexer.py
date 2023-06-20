import re
from pathlib import Path
from .cogs.lexer_utils import split_string_ignore_quotes, find_missing_separator
from .cogs.LexerToken import Token
import fnmatch
from refyre.config import logger

class Lexer:
    '''
        refyre's static lexer 

        Fundamental assumptions:
             - There are 4 spaces / tab. On some systems, there are 8, hence I've made a SPACES_PER_TAB variable that can be adjusted
             - Only one cluster can be specified per line. The lexer is designed to error if someone tries some dumb shit
    '''
    SPACES_PER_TAB = 4

    def preprocess(input_str):
        '''
        Goal: Clean up the new file in preparation 
        for lexical analysis. This means we're going to 
        get rid of the unnecessary clutter.
        '''

        #Remove any multiline comments
        multiline_removal_pattern = r"'''[\s\S]*?'''"
        updated_content = re.sub(multiline_removal_pattern, '', input_str)


        split_lines = updated_content.split('\n')

        #Remove any single line comments
        singleline_removal_pattern = r'#.*$'
        
        updated_content = [re.sub(singleline_removal_pattern, '', l) for l in split_lines] 

        #Remove any purely whitespace lines
        whitespace_pattern = r'^\s*$'

        updated_content = [re.sub(whitespace_pattern, '', l) for l in updated_content]
        updated_content = [l for l in updated_content if l != '']
        updated_content = '\n'.join(updated_content)


        #Remove any stay newlines
        updated_content = re.sub(r'\n+', '\n', updated_content)


        return updated_content

    def extract_line_data(line):
        '''
            Packages all the important line data into a Token()
            object
        '''

        #Extract all data inside the pattern
        #inside_bracket_pattern = r'\[(.*?)\]'
        #inside_bracket_pattern = r'\[(.*?(?=\[(?!.*?\])).*?)\]'
        #inside_bracket_pattern = r'\[(?:[^\[\]]+|(?R))*\]'
        inside_bracket_pattern = r'\[([^[\]]*(?:\[[^[\]]*\])*[^[\]]*)\]'

        #First, ensure the file is properly bracketed.
        p = find_missing_separator(line)
        if p:
            print(f"ERROR: The lexer has found that some of the attributes don't have a '|' between them. This is a necessary, and will directly alter Lexer output if not fixed. Here's the attributes to check for:\n\n ")
            for w in p:
                print(w)

            print(f"\nHere's the line we detected the error on: {line.strip()}")
            print('Make sure that there\'s a bar between all parts. For example, dir="a"name="k" is incorrect, while dir="a"|name="k" is.')
            print('Aborting ...')
            raise Exception("Error in bracketing.")


        try:
            matches = re.search(inside_bracket_pattern, line).group(1)
        except AttributeError as e:
            print(f"ERROR: The lexer attempted to parse line {line} but couldn't find a match. Can you make sure that you have opening and closing brackets? ('[',']')")
            print('Aborting ...')
            raise Exception("Error in parsing lines.")


        match = split_string_ignore_quotes(matches)
        dict_of_args = {}


        #Extract the key and value of each item, while accounting for potential spaces
        extraction_pattern = r'\s*([^=\s]+)\s*=\s*"(.*?)"\s*'
        for arg in match:

            matches = re.match(extraction_pattern, arg)


            try:
                key = matches.group(1)
            except AttributeError as e:
                print("ERROR: it looks like you're missing a key attribute. Check to make sure each attribute and value have an '=' sign between them, and are in \"\".")
                print(f"The error happened on line: {line.strip()}, when we tried to handle match {arg}")
                print('Aborting ...')
                raise Exception("Missing a key attribute")

            try:
                val = matches.group(2)
            except AttributeError as e:
                print("ERROR: it looks like you're missing a val attribute. Check to make sure each attribute and value have an '=' sign between them, and are in \"\".")
                print(f"The error happened on line: {line.strip()}, when we tried to handle match {arg}")
                print('Aborting ...')
                raise Exception("Missing a val attribute")

            dict_of_args[key] = val

        #Grab the tab counts - we grab spaces, and count total
        space_pattern = r'^(\s*)\[.*\]'

        num_spaces = len(re.match(space_pattern, line).group(1))

        if num_spaces % Lexer.SPACES_PER_TAB != 0:
            raise Exception(f"Uneven number of tabs - we assume {Lexer.SPACES_PER_TAB} spaces / tab. If you have a different number (ex: 8 spaces / tab), modify the SPACES_PER_TAB variable.")

        try:
            t = Token(num_spaces // Lexer.SPACES_PER_TAB, **dict_of_args)
        except TypeError as e:
            print(f"ERROR: The lexer failed to read one of the attributes. It's most likely because you typed one of the attributes wrong. Here's the full error message below.")
            print(e)
            print('Aborting ...')
            raise Exception("Lexer failed to read attribute")

        return t

    def lex(input_file):
        '''
            Performs "lexical analysis", a.k.a grabs all the important information 
            from each line
        '''
        if not Path(input_file).exists() or not Path(input_file).is_file():
            raise Exception(f"The input file path to the spec at {input_file} doesn't exist or is a directory!")

        with open(input_file, "r") as f:
            txt = f.read()
            cleaned_lines = Lexer.preprocess(txt)
            cleaned_lines = cleaned_lines.split('\n')

            logger.debug(cleaned_lines)
        tokens = []
        for line in cleaned_lines:
            tokens.append(Lexer.extract_line_data(line))

            
        logger.debug(tokens)
        return tokens

    def __new__(self, input_file):
        return Lexer.lex(input_file)