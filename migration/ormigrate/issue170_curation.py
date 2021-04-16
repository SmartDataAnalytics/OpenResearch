'''
Created on 2021-04-15

@author: wf
'''
from ormigrate.fixer import PageFixer
from ormigrate.rating import Rating

class CurationQualityChecker(PageFixer):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/170
        
    Curation quality check
    '''
        
        
    @classmethod
    def getRating(cls,entityRecord):
        return Rating(7,Rating.missing,'not implemented yet')