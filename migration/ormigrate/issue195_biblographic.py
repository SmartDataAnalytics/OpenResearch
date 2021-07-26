'''
@author: mk
'''

from wikifile.wikiRender import WikiFile
from ormigrate.smw.rating import PageRating, RatingType, EntityRating
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer

class BiblographicFieldFixer(ORFixer):
    '''
    see purpose and issue
        
    '''
    purpose="fixer for Biblographic fields"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/195"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(BiblographicFieldFixer, self).__init__(pageFixerManager)

    def rate(self,rating:EntityRating):
        '''
        Rate Entity by the quality of their biblographic fields
        '''
        return self.getRatingFromWikiFile(rating.wikiFile)

    def getRatingFromWikiFile(self,wikiFile:WikiFile)->PageRating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on
            
        Return:
            Rating: The rating for this WikiFile
        
        '''
        # prepare rating
        wikiText,_eventDict,rating=self.prepareWikiFileRating(wikiFile)
        hasBiblographic = "|has Bibliography=" in wikiText
        hasProceedings  = "|has Proceedings Bibliography=" in wikiText
        if hasProceedings:
            rating.set(7, RatingType.ok,f'Has Proceedings Bibliography field exists which is not defined as a property in OR')
        elif hasBiblographic:
            rating.set(5, RatingType.ok,f'Has Bibliography field exists which is defined as a property in OR but is not used properly')
        else:
            rating.set(1, RatingType.ok, f'No unused Bibliography fields found in event')
        return rating

if __name__ == "__main__":
    PageFixerManager.runCmdLine([BiblographicFieldFixer])
