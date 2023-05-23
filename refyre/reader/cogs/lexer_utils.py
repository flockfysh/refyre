import re

def split_string_ignore_quotes(string):
    pattern = r'"[^"]*"'
    matches = re.findall(pattern, string)

    for match in matches:
        string = string.replace(match, match.replace('|', '\x00'))

    splitted = string.split('|')

    for i in range(len(splitted)):
        splitted[i] = splitted[i].replace('\x00', '|').strip()

    return splitted

def find_missing_separator(string):
    pattern = r'"\s*(\w+)=\S[^"]*"([^|\s])'
    matches = re.findall(pattern, string)
    missing_separators = []

    for match in matches:
        missing_separators.append(match[0])

    return missing_separators