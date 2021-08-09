'''
Created on 2021-04-06

@author: wf
'''
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from corpus.datasources.openresearch import OREventManager
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer

class SeriesFixer(ORFixer):
    '''
    see purpose and issue
    
    '''
    purpose="fixer for event having multiple series marked"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/163"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(SeriesFixer, self).__init__(pageFixerManager)

    def rate(self, rating: EntityRating):
        return self.getRating(rating.getRecord())

    def getRating(self,eventRecord):
        '''
        get the pain Rating for the given event Record
        '''
        if 'inEventSeries' in eventRecord:
            value=eventRecord['inEventSeries']
            if type(value)==list:
                painRating = Rating(9, RatingType.invalid, f'Event Series {value} has multiple objects')
            else:
                painRating = Rating(1, RatingType.ok, f'Event Series is correct for the Event')
        else:
            painRating = Rating(7, RatingType.missing, f'No series found in Event')
        return painRating

    def checkAll(self,askExtra):
        '''
        check if any event has multiple objects in series field
        '''
        """Test if LOD is returned correctly if called from api to store to SQL"""
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventList=OREventManager()
        eventList.debug=self.debug
        eventRecords=eventList.smwHandler.fromWiki(wikiUser,askExtra=askExtra,profile=self.debug)
        count = 0
        for eventRecord in eventRecords:
            # print(str(i['series']) + ":", str(type(i['series'])))
            if 'inEventSeries' in eventRecord:
                value=eventRecord['inEventSeries']
                if type(value)==list:
                    # print (i)
                    count +=1
                    if self.debug: 
                        print(self.generateLink(eventRecord['pageTitle']))
        return count


if __name__ == "__main__":
    PageFixerManager.runCmdLine([SeriesFixer])