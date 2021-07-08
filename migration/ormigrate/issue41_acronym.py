from ormigrate.fixer import PageFixer
from ormigrate.rating import Rating
import re

class AcronymLengthFixer(PageFixer):
    '''
    fixer for acronym length
    https://github.com/SmartDataAnalytics/OpenResearch/issues/41
    '''

    def __init__(self, wikiClient, debug=False, restoreOut=False, suspicitionLength=20):
        '''
        Constructor
        '''
        # call super constructor
        super(AcronymLengthFixer, self).__init__(wikiClient)
        self.debug = debug
        self.restoreOut = restoreOut
        self.suspicitionLength = suspicitionLength

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
            return Rating(7,Rating.missing,'software issue acronym info missing')
        acronym = eventRecord['acronym']
        if acronym is None:
            return Rating(6,Rating.missing,'acronym missing')
        if '"' in acronym:
            return Rating(10,Rating.invalid,'acronym contains double quotes')
        alen=len(acronym)
        if alen < 5:
            return Rating(5,Rating.invalid,f'acronym length {alen}<5')
        elif alen > 45:
            return Rating(4,Rating.invalid,f'acronym length {alen}>45')
        else:
            msg=f'acronym length {alen} in valid range 5-45'
            
        if re.match(r'[A-Z]+\s*[0-9]+', acronym):
            # Regex based on the results of https://cr.bitplan.com/index.php/Acronyms
            return Rating(1,Rating.ok,f'standard acronym with {msg}')
        else:
            return Rating(2,Rating.ok,f'non standard acronym with {msg}')

