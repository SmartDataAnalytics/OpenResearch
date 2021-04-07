from dateutil import parser

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