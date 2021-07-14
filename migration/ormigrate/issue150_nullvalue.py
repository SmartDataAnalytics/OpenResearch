'''
Created on 13.07.2021

@author: wf
'''
from ormigrate.fixer import PageFixerManager,PageFixer
from wikifile.wikiRender import WikiFile
from ormigrate.rating import Rating

class NullValueFixer(PageFixer):
    '''
    Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def __init__(self, wikiFileManager):
        '''
        Constructor
        '''
        super(NullValueFixer, self).__init__(wikiFileManager)
        
    def getRatingFromWikiFile(self,wikiFile:WikiFile)->Rating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on
            
        Return:
            Rating: The rating for this WikiFile
        
        '''
        eventDict=wikiFile.extract_template("Event")
        if eventDict is None:
            rating=Rating(7,Rating.missing,"no event record found")
        else:
            nullValues=0
            wikiText=str(wikiFile)
            nullValues=wikiText.lower().count("::some person")
            if nullValues==0:
                rating=Rating(1,Rating.ok,"no nullValue found")
            elif (nullValues==1):
                rating=Rating(3,Rating.invalid,"found an improper nullValue")
            else:
                rating=Rating(5,Rating.invalid,f"found {nullValues} improper nullValues")    
        return rating
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([NullValueFixer])