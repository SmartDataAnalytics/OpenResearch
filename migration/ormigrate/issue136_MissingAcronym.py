'''
Created on 2021-07-15

@author: wf
'''
from ormigrate.fixer import PageFixerManager,PageFixer
from ormigrate.rating import Rating,RatingType

class EventSeriesAcronymFixer(PageFixer):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/136
    
    fix Missing titles in event Series #136
    ''' 
    
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(EventSeriesAcronymFixer, self).__init__(pageFixerManager)
           
    @classmethod
    def getRating(cls,eventRecord):
        if 'acronym' in eventRecord:
            return Rating(1,RatingType.ok,'acronym available')
        else:
            return  Rating(5,RatingType.missing,'acronym is missing')
        
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([EventSeriesAcronymFixer])