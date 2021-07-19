'''
@author: mk
'''
from ormigrate.rating import Rating,RatingType
from ormigrate.fixer import PageFixer
from wikifile.wikiRender import WikiFile
from ormigrate.rating import PageRating,RatingType

class BiblographicFieldFixer(PageFixer):
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

    def getRatingFromWikiFile(self,wikiFile:WikiFile)->PageRating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on
            
        Return:
            Rating: The rating for this WikiFile
        
        '''
        # prepare rating
        wikiText,_eventDict,rating=self.prepareWikiFileRating(wikiFile,"Event")
        hasBiblographic = "|has Bibliography=" in wikiText
        hasProceedings  = "|has Proceedings Bibliography=" in wikiText
        if hasProceedings:
            painrating = rating.set(7, RatingType.ok,f'Has Proceedings Bibliography field exists which is not defined as a property in OR')
        elif hasBiblographic:
            painrating = rating.set(5, RatingType.ok,f'Has Bibliography field exists which is defined as a property in OR but is not used properly')
        else:
            painrating = rating.set(1, RatingType.ok, f'No unused Bibliography fields found in event')
        return painrating
