import re
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer

class AcronymLengthFixer(ORFixer):
    '''
    see purpose and issue
    
    '''
    purpose="fixer for acronym length"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/41"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(AcronymLengthFixer, self).__init__(pageFixerManager)

    def rate(self, rating: EntityRating):
        return self.getRating(rating.getRecord())

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