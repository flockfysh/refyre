import logging 
from logging.config import fileConfig
from pathlib import Path

'''
Setup for the refyre logger
'''

logging.basicConfig(filename="refyre.log",
                    format='%(levelname)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
 
# Setting the threshold of logger to DEBUG
logger.setLevel(logging.CRITICAL)