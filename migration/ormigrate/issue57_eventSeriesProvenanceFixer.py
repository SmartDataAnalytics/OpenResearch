'''
Created on 2021-04-16

@author: wf
'''
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer
from ormigrate.smw.rating import Rating, RatingType, EntityRating


class EventSeriesProvenanceFixer(ORFixer):
    '''
    see issue and purpose
    '''
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/57"
    purpose="fixes missing provenance information"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(EventSeriesProvenanceFixer, self).__init__(pageFixerManager)

    def rate(self, rating: EntityRating):
        return self.getRating(rating.getRecord())
        
    @classmethod
    def getRating(cls,eventRecord):
        '''
        check the provenance information rating
        '''
        hasDblp=eventRecord.get('dblpSeries') is not  None
        hasWikidata=eventRecord.get('wikidataId') is not None
        if hasDblp and hasWikidata:
            return Rating(0,RatingType.ok,'Gold Standard series')
        if hasDblp:
            return Rating(4,RatingType.ok,'Wikidata id missing for dblp series')
        if hasWikidata:
            return Rating(3,RatingType.ok,'Wikidata only series')
        return Rating(7,RatingType.invalid,'Series provenance data missing')
    
