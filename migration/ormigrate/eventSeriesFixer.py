'''
Created on 2021-04-16

@author: wf
'''
from ormigrate.fixer import PageFixer
from ormigrate.rating import Rating

class EventSeriesProvenanceFixer(PageFixer):
    '''
    fixes Event Series
    '''


    def __init__(self):
        '''
        Constructor
        '''
        
    @classmethod
    def getRating(cls,eventRecord):
        hasDblp=eventRecord.get('dblpSeries') is not  None
        hasWikidata=eventRecord.get('wikidataId') is not None
        if hasDblp and hasWikidata:
            return Rating(1,Rating.ok,'Gold Standard series')
        if hasDblp:
            return Rating(4,Rating.ok,'Wikdata id missing for dblp series')
        if hasWikidata:
            return Rating(3,Rating.ok,'Wikdata only series')
        return Rating(5,Rating.invalid,'Series provenance data missing')
    
        