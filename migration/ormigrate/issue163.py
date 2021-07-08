'''
Created on 2021-04-06

@author: wf
'''
from ormigrate.fixer import PageFixer
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.rating import Rating
from openresearch.event import EventList

class SeriesFixer(PageFixer):
    '''
    fixer for Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/163
    '''

    def __init__(self, wikiClient, debug=False):
        '''
        Constructor
        '''
        # call super constructor
        super(SeriesFixer, self).__init__(wikiClient)
        self.debug = debug


    def getRating(self,eventRecord):
        painrating = None
        if 'inEventSeries' in eventRecord:
            value=eventRecord['inEventSeries']
            if type(value)==list:
                painRating = Rating(9, Rating.invalid, f'Event Series {value} has multiple objects')
            else:
                painRating = Rating(1, Rating.ok, f'Event Series is correct for the Event')
        else:
            painRating = Rating(7, Rating.missing, f'No series found in Event')
        return painRating

    def checkAll(self,askExtra):
        '''
        check if any event has multiple objects in series field
        '''
        """Test if LOD is returned correctly if called from api to store to SQL"""
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventList=EventList()
        eventList.debug=self.debug
        eventRecords=eventList.fromWiki(wikiUser,askExtra=askExtra,profile=self.debug)
        count = 0
        for eventRecord in eventRecords:
            # print(str(i['series']) + ":", str(type(i['series'])))
            if 'inEventSeries' in eventRecord:
                value=eventRecord['inEventSeries']
                if eventRecord['pageTitle'] == 'IJCAI-PRICAI 2020':
                    print(eventRecord)
                if type(value)==list:
                    # print (i)
                    count +=1
                    if self.debug: 
                        print(self.generateLink(eventRecord['pageTitle']))
        return count


if __name__ == "__main__":
    fixer = SeriesFixer(debug=True)
    count=fixer.checkAll("")
    print(count)