'''
Created on 2021-04-16

@author: wf
'''
from openresearch.event import EventList,EventSeriesList
class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
        
    def fromWikiUser(self,wikiUser):
        '''
        get events with series by knitting / linking the entities together
        '''
        self.eventList=EventList()
        self.eventList.debug=self.debug
        self.eventList.fromCache(wikiUser)
        
        self.eventSeriesList=EventSeriesList()
        self.eventSeriesList.debug=self.debug
        self.eventSeriesList.fromCache(wikiUser)
        
        # get foreign key hashtable
        self.seriesLookup=self.eventList.getLookup("inEventSeries", withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup=self.eventSeriesList.getLookup("acronym",withDuplicates=True)
        
        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents=self.seriesLookup[seriesAcronym]
                print(f"{seriesAcronym}:{len(seriesEvents):4d}" )
            else:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print ("%d events/%d eventSeries -> %d linked" % (len(self.eventList.getList()),len(self.eventSeriesList.getList()),len(self.seriesLookup)))
    
    