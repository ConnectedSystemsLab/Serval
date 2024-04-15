"""
Code to log events to process data.
"""

import const
from src.utils import Time


def clear_logging_file():
    with open(const.LOGGING_FILE, "w+") as out:
        out.write("")
        out.close()

#import logging and set it up
 
from fastlogging import LogInit, INFO, Logger

clear_logging_file()
loggingCurrentTime = Time() ##will be updated by the simulator class
currentTimeStr = loggingCurrentTime.to_str() 

Logger.cbFormatter = lambda self, entry: f'{entry[3]}'
logger = LogInit(pathName=const.LOGGING_FILE, level=INFO, encoding="ascii", useThreads=True) #https://github.com/brmmm3/fastlogging/blob/master/doc/API.rst

#main logging function:
def Log(description: str, *args) -> None:
    global logger
    global loggingCurrentTime
    logger.info(loggingCurrentTime.to_str() + "\t" + description + "\t" + "\t".join([str(x) for x in args]))

def update_logging_file():
    global logger
    logger.flush()

def update_logging_time(time: Time):
    global loggingCurrentTime
    loggingCurrentTime = time.copy()
    global currentTimeStr
    currentTimeStr = loggingCurrentTime.to_str()
def get_logging_time():
    global loggingCurrentTime
    return loggingCurrentTime.copy()
    
def close_logging_file():
    global logger
    logger.stop(now=False)
    logger.shutdown()