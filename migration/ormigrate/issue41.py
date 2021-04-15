from ormigrate.fixer import PageFixer
import re

class AcronymLengthFixer(PageFixer):
    '''
    fixer for acronym length
    https://github.com/SmartDataAnalytics/OpenResearch/issues/41
    '''

    def __init__(self, wikiId="or", baseUrl="https://www.openresearch.org/wiki/", debug=False, restoreOut=False, suspicitionLength=20):
        '''
        Constructor
        '''
        # call super constructor
        super(AcronymLengthFixer, self).__init__(wikiId, baseUrl)
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
            return 6
        acronym = eventRecord['acronym']
        if acronym is None:
            return 6
        elif re.match(r'[A-Z]+\s*[0-9]+', acronym):
            # Regex based on the results of https://cr.bitplan.com/index.php/Acronyms
            if len(acronym) < 5:
                return 5
            elif len(acronym) > 45:
                return 5
            else:
                return 1
        else:
            return 6

