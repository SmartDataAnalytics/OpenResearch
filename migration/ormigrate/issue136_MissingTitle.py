'''
Created on 2021-07-15

@author: wf
'''
from ormigrate.fixer import PageFixerManager,PageFixer
from ormigrate.rating import Rating

class EventSeriesTitleFixer(PageFixer):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/136
    
    fix Missing titles in event Series #136
    ''' 
    
    def __init__(self, wikiFileManager):
        '''
        Constructor
        '''
        super(EventSeriesTitleFixer, self).__init__(wikiFileManager)
           
    @classmethod
    def getRating(cls,eventRecord):
        if 'title' in eventRecord:
            return Rating(1,Rating.ok,'title available')
        else:
            return  Rating(5,Rating.missing,'title is missing')
        
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([EventSeriesTitleFixer])