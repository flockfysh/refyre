'''
Setup for the refyre logger
'''


logname = 'refyre.log'

logfile = open(logname, 'w')

def log(*args, level = "[INFO]"):
    print(level, *args, file = logfile)