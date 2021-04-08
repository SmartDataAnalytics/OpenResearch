from dateutil import parser
import os
from migrate.Dictionary import Dictionary

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