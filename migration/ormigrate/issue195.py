'''
@author: mk
'''
import re
from ormigrate.rating import Rating
from ormigrate.fixer import PageFixer

class BiblographicFieldFixer(PageFixer):
    '''
        fixer for Acceptance Rate Not calculated
        https://github.com/SmartDataAnalytics/OpenResearch/issues/195
    '''

    def __init__(self, wikiClient,debug=False):
        '''
                Constructor
                '''
        # call super constructor
        super(BiblographicFieldFixer, self).__init__(wikiClient)
        self.debug = debug
        self.nosub = 0
        self.noacc = 0
        self.painrating = None

    @classmethod
    def getRating(self, eventRecord):
        painrating = None
        hasBiblographic = False
        hasProceedings  = False
        for key in eventRecord:
            checker = str(key).lower()
            if checker.find("bibliography") != -1:
                if checker.find('proceedings') != -1:
                    hasProceedings = True
                else:
                    hasBiblographic= True
        if hasProceedings:
            painrating = Rating(7, Rating.ok,f'Has Proceedings Bibliography field exists which is not defined as a property in OR')
        elif hasBiblographic:
            painrating = Rating(5, Rating.ok,f'Has Bibliography field exists which is defined as a property in OR but is not used properly')
        else:
            painrating = Rating(1, Rating.ok, f'Bibliography field not found in event')
        return painrating
