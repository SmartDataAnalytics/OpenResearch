'''
Created on 2021-04-16

@author: wf
'''
from ormigrate.fixer import PageFixer
from ormigrate.rating import Rating, RatingType

class EventSeriesProvenanceFixer(PageFixer):
    '''
    fixes Event Series
    '''

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(EventSeriesProvenanceFixer, self).__init__(pageFixerManager)
        
    @classmethod
    def getRating(cls,eventRecord):
        hasDblp=eventRecord.get('dblpSeries') is not  None
        hasWikidata=eventRecord.get('wikidataId') is not None
        if hasDblp and hasWikidata:
            return Rating(0,RatingType.ok,'Gold Standard series')
        if hasDblp:
            return Rating(4,RatingType.ok,'Wikidata id missing for dblp series')
        if hasWikidata:
            return Rating(3,RatingType.ok,'Wikidata only series')
        return Rating(7,RatingType.invalid,'Series provenance data missing')
    
