'''
Created on 13.07.2021

@author: wf
'''
from ormigrate.fixer import PageFixerManager,PageFixer
from wikifile.wikiRender import WikiFile
from ormigrate.rating import PageRating,RatingType


class NullValueFixer(PageFixer):
    '''
    Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(NullValueFixer, self).__init__(pageFixerManager)
        
    def getRatingFromWikiFile(self,wikiFile:WikiFile)->PageRating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on
            
        Return:
            Rating: The rating for this WikiFile
        
        '''
        # prepare rating
        wikiText,eventDict,rating=self.prepareWikiFileRating(wikiFile,"Event")
        # start rating
        if eventDict is None:
            rating.set(7,RatingType.missing,"no event record found")
        else:
            nullValues=0
            nullValues=wikiText.lower().count("::some person")
            if nullValues==0:
                rating.set(1,RatingType.ok,"no nullValue found")
            elif (nullValues==1):
                rating.set(3,RatingType.invalid,"found an improper nullValue")
            else:
                rating.set(5,RatingType.invalid,f"found {nullValues} improper nullValues")    
        return rating
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([NullValueFixer])