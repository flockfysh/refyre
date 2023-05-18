import re
from pathlib import Path

class Token:
    '''
        A single Lexer token
    '''
    def __init__(self, tab_level, pattern = "", dir = "",  type = "", name = "", flags = ""):
        self.tab_level = tab_level
        self.pattern = pattern
        self.directory = dir
        self.dirtype = type
        self.name = name
        self.flags = flags

    def __repr__(self):
        return f"Token(tab_level={self.tab_level},pattern={self.pattern},directory={self.directory},dirtype={self.dirtype},name={self.name},flags={self.flags})"

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

        #Remove any single line comments
        singleline_removal_pattern = r'#.*$'
        updated_content = re.sub(singleline_removal_pattern, '', updated_content)

        #Remove any purely whitespace lines
        whitespace_pattern = r'^\s*$'
        updated_content = re.sub(whitespace_pattern, '', updated_content).strip()

        #Remove any stay newlines
        updated_content = re.sub(r'\n+', '\n', updated_content)
        return updated_content

    def extract_line_data(line):
        '''
            Packages all the important line data into a Token()
            object
        '''

        #Extract all data inside the pattern
        inside_bracket_pattern = r'\[(.*?)\]'

        matches = re.findall(inside_bracket_pattern, line)

        #Rule: Only one cluster per line
        if len(matches) > 1:
            raise Exception("You can only specify one cluster per line!")

        match = matches[0].split('|')
        dict_of_args = {}

        #Extract the key and value of each item, while accounting for potential spaces
        extraction_pattern = r'\s*([^=\s]+)\s*=\s*"(.*?)"\s*'
        for arg in match:

            matches = re.match(extraction_pattern, arg)

            key = matches.group(1)
            val = matches.group(2)

            dict_of_args[key] = val

        #Grab the tab counts - we grab spaces, and count total
        space_pattern = r'^(\s*)\[.*\]'

        num_spaces = len(re.match(space_pattern, line).group(1))

        if num_spaces % Lexer.SPACES_PER_TAB != 0:
            raise Exception(f"Uneven number of tabs - we assume {Lexer.SPACES_PER_TAB} spaces / tab. If you have a different number (ex: 8 spaces / tab), modify the SPACES_PER_TAB variable.")

        return Token(num_spaces // Lexer.SPACES_PER_TAB, **dict_of_args)

    def lex(input_file):
        '''
            Performs "lexical analysis", a.k.a grabs all the important information 
            from each line
        '''
        if not Path(input_file).exists():
            raise Exception(f"The input file path to the spec at {input_file} doesn't exist!")

        with open(input_file, "r") as f:
            txt = f.read()
            cleaned_lines = Lexer.preprocess(txt)
            cleaned_lines = cleaned_lines.split('\n')

        tokens = []
        for line in cleaned_lines:
            tokens.append(Lexer.extract_line_data(line))
            
        return tokens
