'''
Created on 2021-04-06

@author: wf
'''
import dateutil.parser
import re
from ormigrate.fixer import PageFixer,PageFixerManager
from ormigrate.rating import Rating,RatingType


class DateFixer(PageFixer):
    '''
    see purpose and issue
    '''
    purpose="fixer for Dates being in incorrect format"
    issue=" https://github.com/SmartDataAnalytics/OpenResearch/issues/71"
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(DateFixer, self).__init__(pageFixerManager)
        
    def parseDate(self,date):
        '''
        parses the date in any format to the format YYYY/MM/DD
        Args:
            date: Given date in any format
        Returns:
            date(str): Date in YYYY/MM/DD format. None if date cannot be converted
        '''
        try:
            parseToDatetime = dateutil.parser.parse(date)
        except ValueError as _e:
            return None
        datetimeToDate = parseToDatetime.date()
        datetimetoString = datetimeToDate.strftime("%Y/%m/%d")
        return datetimetoString
        

    def fixEventRecord(self, event, datelist=['Start date' , 'End date'], errors=None):
        if errors is None:
            errors={}
        for element in datelist:
            eventDate = event.get(element)
            if eventDate is not None:
                fixedDate = self.parseDate(eventDate)
                if fixedDate is not None:
                    if fixedDate != eventDate:
                        event[element] = fixedDate
                else:
                    errors['fixNotPossible']=True
            else:
                key= element+'notFound'
                errors[key]= True
        if self.debug and errors.get('fixNotPossible'): print(self.generateLink(event['pageTitle']))
        return event,errors


    def getFixedDateWikiFile(self, page, event, datetype='date'):
        '''
        fix the date of the given page and event and mark unfixable pages
        Returns:
            Fixed text of the page.
        '''
        generateLink=False
        change=False
        dates = re.findall('|.*'+datetype+'.*=.*\n', event)
        if len(dates) != 0:
            for element in dates:
                name,value=self.getNameValue(element)
                if name is not None and value is not None:
                    fixedDate = self.parseDate(value)
                    if fixedDate is not None:
                        if fixedDate != value:
                            change = True
                        event = event.replace(element,'|'+name+'='+fixedDate)
                    else:
                        generateLink=True
        if self.debug and generateLink: print(self.generateLink(page))
        if change:
            return event
        else:
            return None
        
    @classmethod
    def getRating(self,eventRecord):
        '''
        get the pain Rating for the given eventRecord
        '''
        # TODO add checks for invalid dates that are not properly formatted examples
        painrating= None
        startDate = None
        endDate = None
        if 'startDate' in eventRecord: startDate = eventRecord['startDate']
        if 'endDate' in eventRecord: endDate = eventRecord['endDate']

        if startDate is not None and endDate is not None:
            painrating= Rating(1,RatingType.ok,f'Dates,  {startDate} , {endDate} valid')
        elif startDate is None and endDate is None:
            painrating=Rating(5,RatingType.missing,f'Dates not found')
        elif startDate is None and endDate is not None:
            painrating=Rating(7,RatingType.missing,f'Start Date is not there while end date exists')
        elif startDate is not None and endDate is None:
            painrating=Rating(3,RatingType.missing,f'Start Date is there but end date is not')
        return painrating

if __name__ == "__main__":
    PageFixerManager.runCmdLine([DateFixer])
