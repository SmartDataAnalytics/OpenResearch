from ormigrate.fixer import PageFixer,PageFixerManager
from ormigrate.rating import Rating,PageRating,RatingType
from wikifile.wikiFile import WikiFile
import re

class AcronymLengthFixer(PageFixer):
    '''
    fixer for acronym length
    https://github.com/SmartDataAnalytics/OpenResearch/issues/41
    '''

    def __init__(self, wikiFileManager):
        '''
        Constructor
        '''
        super(AcronymLengthFixer, self).__init__(wikiFileManager)
        
    def getRatingFromWikiFile(self,wikiFile:WikiFile)->PageRating:
        '''
        Args:
            wikiFile(WikiFile): the wikiFile to work on
            
        Return:
            Rating: The rating for this WikiFile
        
        '''
        # prepare rating
        _wikiText,eventRecord,rating=self.prepareWikiFileRating(wikiFile,"Event")
        arating=AcronymLengthFixer.getRating(eventRecord)
        rating.set(arating.pain,arating.reason,arating.hint)
        return rating

    @staticmethod
    def getRating(eventRecord):
        '''
        Returns the pain scale of this event
        https://cr.bitplan.com/index.php/Acronyms

        Args:
            eventRecord:

        Returns:
            int: pain rating of the acronym
        '''
        if 'acronym' not in eventRecord:
            return Rating(7,RatingType.missing,'software issue acronym info missing')
        acronym = eventRecord['acronym']
        if acronym is None:
            return Rating(6,RatingType.missing,'acronym missing')
        if '"' in acronym:
            return Rating(10,RatingType.invalid,'acronym contains double quotes')
        alen=len(acronym)
        if alen < 5:
            return Rating(5,RatingType.invalid,f'acronym length {alen}<5')
        elif alen > 45:
            return Rating(4,RatingType.invalid,f'acronym length {alen}>45')
        else:
            msg=f'acronym length {alen} in valid range 5-45'
            
        if re.match(r'[A-Z]+\s*[0-9]+', acronym):
            # Regex based on the results of https://cr.bitplan.com/index.php/Acronyms
            return Rating(1,RatingType.ok,f'standard acronym with {msg}')
        else:
            return Rating(2,RatingType.ok,f'non standard acronym with {msg}')

if __name__ == '__main__':
    PageFixerManager.runCmdLine([AcronymLengthFixer])