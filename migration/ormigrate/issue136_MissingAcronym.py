'''
Created on 2021-07-15

@author: wf
'''
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer, Entity


class EventSeriesAcronymFixer(ORFixer):
    '''
    see purpose and issue
    ''' 
    purpose="fix missing acronyms in event Series"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/136"

    worksOn = [Entity.EVENT_SERIES]
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(EventSeriesAcronymFixer, self).__init__(pageFixerManager)


    def rate(self, rating: EntityRating):
        if hasattr(rating.entity, 'acronym') and getattr(rating.entity, 'acronym'):
            rating.set(1,RatingType.ok,'acronym available')
            return
        elif rating.wikiFile is not None:
            rawRecords=rating.getRawRecords()
            if 'acronym' in rawRecords and rawRecords.get('acronym'):
                rating.set(2,RatingType.ok,'acronym available but propertyname incorrrect')
                return
        rating.set(5,RatingType.missing,'acronym is missing')
           
    @classmethod
    def getRating(cls,eventRecord):
        if 'acronym' in eventRecord:
            return Rating(1,RatingType.ok,'acronym available')
        else:
            return Rating(5,RatingType.missing,'acronym is missing')

    def fix(self,rating:EntityRating):
        '''
        Fixes the missing acronyms of event series
        Args:
            rating: EntityRating to be fixed

        Returns:

        '''
        rawRecords = rating.getRawRecords()
        if hasattr(rating.entity, "acronym") and getattr(rating.entity, 'acronym'):
            pass
        else:
            # normalized acronym value is missing
            if "acronym" in rawRecords and rawRecords.get('acronym').strip():
                acronym=rawRecords.get("acronym")
                if acronym:
                    acronym.strip()
                setattr(rating.entity, "acronym", acronym)
                return
            else:
                # Try to get event series acronym from pageTitle
                pass
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([EventSeriesAcronymFixer])