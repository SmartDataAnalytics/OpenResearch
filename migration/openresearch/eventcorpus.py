'''
Created on 2021-04-16

@author: wf
'''
from openresearch.event import EventList,EventSeriesList
from pathlib import Path
class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug

    def fromWikiSonBackupFiles(self,backupdir=str(Path.home() / 'wikibackup'/ 'or' ),wikiId='or',listOfItems=[]):
        '''
               get events with series by knitting / linking the entities together
        '''
        self.eventList = EventList()
        self.eventList.debug = self.debug
        self.eventList.fromWikiSonBackupFiles("Event",backupdir=backupdir,wikiId=wikiId,listOfItems=listOfItems)

        self.eventSeriesList = EventSeriesList()
        self.eventSeriesList.debug = self.debug
        self.eventSeriesList.fromWikiSonBackupFiles("Event series",backupdir=backupdir,wikiId=wikiId,listOfItems=listOfItems)

        # get foreign key hashtable
        self.seriesLookup = self.eventList.getLookup("Series", withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup = self.eventSeriesList.getLookup("acronym", withDuplicates=True)

        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents=self.seriesLookup[seriesAcronym]
                print(f"{seriesAcronym}:{len(seriesEvents):4d}" )
            else:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print ("%d events/%d eventSeries -> %d linked" % (len(self.eventList.getList()),len(self.eventSeriesList.getList()),len(self.seriesLookup)))
        
    def fromWikiUser(self,wikiUser,propertyList=[]):
        '''
        get events with series by knitting / linking the entities together
        '''
        self.eventList=EventList()
        self.eventList.debug=self.debug
        if len(propertyList) != 0:
            self.eventList.propertyLookupList=propertyList
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

    def getEventsInSeries(self,seriesAcronym):
        if seriesAcronym in self.seriesAcronymLookup:
            seriesEvents = self.seriesLookup[seriesAcronym]
            if self.debug:
                print(f"{seriesAcronym}:{len(seriesEvents):4d}")
        else:
            if self.debug:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
            return None
        return seriesEvents
