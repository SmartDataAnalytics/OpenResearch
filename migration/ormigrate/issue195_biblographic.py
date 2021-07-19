'''
@author: mk
'''
from ormigrate.rating import Rating,RatingType
from ormigrate.fixer import PageFixer

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
            painrating = Rating(7, RatingType.ok,f'Has Proceedings Bibliography field exists which is not defined as a property in OR')
        elif hasBiblographic:
            painrating = Rating(5, RatingType.ok,f'Has Bibliography field exists which is defined as a property in OR but is not used properly')
        else:
            painrating = Rating(1, RatingType.ok, f'Bibliography field not found in event')
        return painrating
