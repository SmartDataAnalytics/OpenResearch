'''
Created on 2021-07-15

@author: wf
'''
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer

class EventSeriesAcronymFixer(ORFixer):
    '''
    see purpose and issue
    ''' 
    purpose="fix missing acronyms in event Series"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/136"
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(EventSeriesAcronymFixer, self).__init__(pageFixerManager)

    def rate(self, rating: EntityRating):
        return self.getRating(rating.getRecord())
           
    @classmethod
    def getRating(cls,eventRecord):
        if 'acronym' in eventRecord:
            return Rating(1,RatingType.ok,'acronym available')
        else:
            return  Rating(5,RatingType.missing,'acronym is missing')
        
    #TODO
    # implement fixer e.g. by getting the acronym of the series elements and removing the year

    # The Series property of event uses currently the pageTitle of the EventSeries as value space
    # If we NOT use the pageTitle as acronym how can we identify the elements of an series?
        
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([EventSeriesAcronymFixer])