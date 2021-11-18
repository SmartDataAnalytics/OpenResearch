'''
Created on 2021-04-06

@author: wf
'''
import dateutil.parser
import re
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer, Entity


class DateFixer(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="fixer for Dates being in incorrect format"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/71"

    worksOn = [Entity.EVENT]
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(DateFixer, self).__init__(pageFixerManager)

    @staticmethod
    def parseDate(date:str):
        '''
        parses the date in any format to the format YYYY-MM-DD (iso-format see https://www.semantic-mediawiki.org/wiki/Help:Type_Date)
        Args:
            date: Given date in any format
        Returns:
            date(str): Date in YYYY-MM-DD format. None if date cannot be converted
        '''
        errors= {}
        if date:
            if re.match("^(19|20)\d{2}$", date.strip()):
                errors["onlyYear"]="Only the year is en as input the parsed date will be the given year and month & day from the time of cumputation"
        try:
            parseToDatetime = dateutil.parser.parse(date)
        except ValueError or TypeError as _e:
            errors[date] = _e
            return None,errors
        datetimeToDate = parseToDatetime.date()
        datetimetoString = datetimeToDate.strftime("%Y-%m-%d")
        return datetimetoString,errors

    def fix(self,rating:EntityRating):
        record=rating.getRecord()
        self.fixEventRecord(record, datelist=["startDate", "endDate"])

    def fixEventRecord(self, event, datelist=None, errors=None):
        if datelist is None:
            datelist = ['Start date', 'End date']
        if errors is None:
            errors={}
        for element in datelist:
            eventDate = event.get(element)
            if eventDate is not None:
                fixedDate,parseError = self.parseDate(eventDate)
                if len(parseError)==0:
                    if fixedDate != eventDate:
                        event[element] = fixedDate
                elif "onlyYear" in parseError:
                    # eventDate is only a year → move property value to the property year
                    event["year"]=eventDate
                    event[element] = None
                else:
                    errors['fixNotPossible']=True
                    event[element]=None
            else:
                key= element+'notFound'
                errors[key]= True
        if self.debug and errors.get('fixNotPossible'): print(self.generateLink(event['pageTitle']))
        return event,errors

    @classmethod
    def isIso(cls, date:str):
        """
        checks if given date is in iso format yyyy-mm-dd
        Args:
            date:

        Returns:
            bool
        """
        try:
            parsedDate=dateutil.parser.isoparse(date)
            return True
        except Exception as e:
            return False
        
    @classmethod
    def checkDate(cls,dateStr)->(int,str):
        if dateStr is None or dateStr.strip()=="":
            return 5,"Date is missing"
        else:
            _date,errors = cls.parseDate(dateStr)
            if len(errors)==0:
                if cls.isIso(dateStr):
                    return 1,"Date {dateStr} is ok"
                else:
                    return 3, "Date {dateStr} is not in iso format but valid date"
            elif "onlyYear" in errors:
                return 4, f"Date '{dateStr}' is only a year (property value can be ed over to year property)"
            else:
                return 7,f"Date '{dateStr}' can't be parsed: {errors[dateStr]}"

    @classmethod
    def durationValid(cls, startdate, enddate) -> bool:
        """
        Checks if the given dates form a valid duration for an event (0 - 100 days)
        Args:
            startdate: start date
            enddate: end date

        Returns:
            bool
        """
        startdate=dateutil.parser.parse(startdate)
        enddate=dateutil.parser.parse(enddate)
        duration=enddate-startdate
        if duration.days<0 or duration.days>100:
            return False
        else:
            return True

    def rate(self, rating: EntityRating):
        aRating = self.getRating(rating.getRecord())
        rating.set(pain=aRating.pain, reason=aRating.reason, hint=aRating.hint)
        return rating

    @classmethod
    def getRating(self,eventRecord):
        '''
        get the pain Rating for the given eventRecord
        '''
        # TODO add checks for invalid dates that are not properly formatted examples
        painrating= None
        startDate = eventRecord.get('startDate')
        endDate = eventRecord.get('endDate')
        painStartDate, messageStartDate = self.checkDate(startDate)
        painEndDate, messageEndDate = self.checkDate(endDate)
        maxPain=max(painStartDate, painEndDate)
        additionalHint=""
        if maxPain == 1 or maxPain == 3:
            if not self.durationValid(startDate, endDate):
                additionalHint+="The duration of the event is invalid! Please check start- and endDate"
                maxPain=4
                ratingType = RatingType.invalid
            else:
                ratingType = RatingType.ok

        elif maxPain == 4:
            ratingType = RatingType.missing
        elif maxPain == 5:
            ratingType = RatingType.missing
        else:
            ratingType = RatingType.invalid
        return Rating(maxPain,ratingType,f"{additionalHint} startdate: {messageStartDate} endDate: {messageEndDate}")

if __name__ == "__main__":
    PageFixerManager.runCmdLine([DateFixer])
