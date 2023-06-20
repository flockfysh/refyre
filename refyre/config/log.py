import logging 
from logging.config import fileConfig
from pathlib import Path

'''
Setup for the refyre logger
'''

logging.basicConfig(filename="refyre2.log",
                    format='%(levelname)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.DEBUG)




#Current logger
logname = 'refyre.log'
logfile = open(logname, 'w')

def log(*args, level = "[INFO]"):
    print(level, *args, file = logfile)