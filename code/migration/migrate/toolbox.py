from dateutil import parser
import os
from migrate.Dictionary import Dictionary
from pathlib import Path

def parseDate(date):
    '''
    parses the date in any format to the format YYYY/MM/DD
    Args:
        date: Given date in any format
    Returns:
        date(str): Date in YYYY/MM/DD format. None if date cannot be converted
    '''
    try:
        parseToDatetime = parser.parse(date)
    except ValueError as e:
        return None
    datetimeToDate = parseToDatetime.date()
    datetimetoString = datetimeToDate.strftime("%Y/%m/%d")
    return datetimetoString


def loadDictionary():
    path = os.path.dirname(__file__) + "/../../dataset/dictionary.yaml"
    lookup_dict = Dictionary(path)
    return lookup_dict


def ensureDirectoryExists(directory):
    '''
    Given a path ensures the directory exists. New directory will be made if it doesn't exist
    Args:
        directory(str): PAth to directory
    '''
    Path(directory).mkdir(parents=True, exist_ok=True)


def getHomePath(localPath):
    '''
    get the given home path
    '''
    homePath=str(Path.home() / localPath)
    ensureDirectoryExists(homePath)
    return homePath