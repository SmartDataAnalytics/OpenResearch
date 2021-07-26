'''
Created on 2021-04-06

@author: wf
'''
import dateutil.parser
import re
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer


class DateFixer(ORFixer):
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
        errors= {}
        try:
            parseToDatetime = dateutil.parser.parse(date)
        except ValueError as _e:
            errors[date] = _e
            return None,errors
        datetimeToDate = parseToDatetime.date()
        datetimetoString = datetimeToDate.strftime("%Y/%m/%d")
        return datetimetoString,errors
        

    def fixEventRecord(self, event, datelist=['Start date' , 'End date'], errors=None):
        if errors is None:
            errors={}
        for element in datelist:
            eventDate = event.get(element)
            if eventDate is not None:
                fixedDate,parseError = self.parseDate(eventDate)
                if len(parseError) == 0:
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
    def checkDate(cls,dateStr)->(int,str):
        if dateStr is None or dateStr.strip()=="":
            return 5,"Date is missing"
        else:
            _date,errors = cls.parseDate(cls, dateStr)
            if len(errors) == 0:
                return 1,"Date is {dateStr} is ok"
            else:
                return 7,f"Date '{dateStr}' can't be parsed: {errors[dateStr]}"

    def rate(self, rating: EntityRating):
        return self.getRating(rating.getRecord())

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
        painStartDate, messageStartDate = self.checkDate(startDate)
        painEndDate, messageEndDate = self.checkDate(endDate)

        if painStartDate == 1 and painEndDate == 1:
            painrating= Rating(1,RatingType.ok,f'Dates,  {startDate} , {endDate} valid')
        elif painStartDate == 7:
            painrating= Rating(7,RatingType.invalid,f"{messageStartDate}")
        elif painEndDate == 7:
            painrating = Rating(7, RatingType.invalid,f"{messageEndDate}")
        elif painStartDate != 1 and painEndDate != 1:
            painrating=Rating(5,RatingType.missing,f'Dates not found')
        elif painStartDate == 5 and painEndDate == 1:
            painrating=Rating(7,RatingType.missing,f'Start Date missing for valid end date {endDate}')
        elif painStartDate == 1 and painEndDate == 5:
            painrating=Rating(3,RatingType.missing,f'End Date missing for valid start date {startDate}')
        return painrating

if __name__ == "__main__":
    PageFixerManager.runCmdLine([DateFixer])
