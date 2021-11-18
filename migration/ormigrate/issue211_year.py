'''
Created on 2021-11-17

@author: th
'''
import re

from ormigrate.issue71_date import DateFixer
from ormigrate.smw.rating import RatingType, EntityRating
from ormigrate.fixer import ORFixer, Entity


class YearFixer(ORFixer):
    '''
    see purpose and issue
    Notes:
        * Which year does a event has if it startDate and endDate have different years?
    '''
    purpose="fixer for year property"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/211"

    worksOn = [Entity.EVENT]

    YEAR_PROP="year"
    YEAR_REGEX="^(19|20)\d{2}$"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(YearFixer, self).__init__(pageFixerManager)


    def fix(self, rating:EntityRating):
        """
        Sets the year property if missing or incorrect.
        Args:
            entityRating: entity for which that should be fixed

        Returns:
            Nothing
        """
        records = rating.getRecord()
        if self.YEAR_PROP in records and records.get(self.YEAR_PROP):
            # year property is present and set → check id valid
            if re.match(self.YEAR_REGEX, str(records.get(self.YEAR_PROP))):
                # year property is set and valid → end fixing
                return
            else:
                # value is invalid set to none
                records[self.YEAR_PROP] = None
        # year property is missing → check if it could be reconstructed from start or end date
        otherYearSources = [record for record in [records.get("startDate", None), records.get("endDate", None)] if record is not None]
        possibleYears = [date[:4] for date, errors in [DateFixer.parseDate(d) for d in otherYearSources] if len(errors) == 0]  # depends on returned iso format of the date
        if any(possibleYears):
            records[self.YEAR_PROP] = str(min([int(year) for year in possibleYears]))   #ToDo: Is year in normalized form int or string?



    def rate(self, rating: EntityRating):
        """
        rates given entity for the quality of the year property
        Args:
            rating: entity for which that should be rated

        Returns:
            EntityRating
        """
        records=rating.getRecord()
        if self.YEAR_PROP in records and records.get(self.YEAR_PROP):
            # year property is present and set → check id valid
            if re.match(self.YEAR_REGEX, str(records.get(self.YEAR_PROP))):
                rating.set(pain=0, reason=RatingType.ok, hint="Year property is set and valid")
            else:
                rating.set(pain=5, reason=RatingType.invalid, hint="Year property is set but invalid")
        else:
            # year property is missing → check if it could be reconstructed from start or end date
            otherYearSources=[record for record in [records.get("startDate", None), records.get("endDate", None)] if record is not None]
            if any([len(errors)==0 for data, errors in [DateFixer.parseDate(d) for d in otherYearSources]]):
                rating.set(pain=3, reason=RatingType.missing, hint="Year property is missing but can be derived from other properties")
            else:
                rating.set(pain=8, reason=RatingType.missing,hint="Year property is missing")
        return rating