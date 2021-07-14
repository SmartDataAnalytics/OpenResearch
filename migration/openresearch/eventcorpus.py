'''
Created on 2021-04-16

@author: wf
'''
from openresearch.event import EventList,EventSeriesList
from ormigrate.toolbox import HelperFunctions as hf
from os.path import expanduser
from lodstorage.csv import CSV
from lodstorage.lod import LOD

class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False):
        '''
        Constructor
        '''
        self.debug=debug
                

    def fromWikiFileManager(self,wikiFileManager):
        '''
            get events with series by knitting / linking the entities together
        '''
        self.eventList = EventList()
        self.eventList.debug = self.debug
        self.eventList.fromWikiFileManager(wikiFileManager)

        self.eventSeriesList = EventSeriesList()
        self.eventSeriesList.debug = self.debug
        self.eventSeriesList.fromWikiFileManager(wikiFileManager)
        
        # get foreign key hashtable
        self.seriesLookup = LOD.getLookup(self.eventList.getList(),"Series", withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup = LOD.getLookup(self.eventSeriesList.getList(),"acronym", withDuplicates=True)

        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents=self.seriesLookup[seriesAcronym]
                if self.debug:
                    print(f"{seriesAcronym}:{len(seriesEvents):4d}" )
            else:
                if self.debug:
                    print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print ("%d events/%d eventSeries -> %d linked" % (len(self.eventList.getList()),len(self.eventSeriesList.getList()),len(self.seriesLookup)))
        
    def fromWikiUser(self,wikiUser,propertyList=[],force=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        self.eventList=EventList()
        self.eventList.debug=self.debug
        if len(propertyList) != 0:
            self.eventList.propertyLookupList=propertyList
        self.eventList.fromCache(wikiUser,force=force)
        
        self.eventSeriesList=EventSeriesList()
        self.eventSeriesList.debug=self.debug
        self.eventSeriesList.fromCache(wikiUser,force=force)
        
        # get foreign key hashtable
        self.seriesLookup=self.eventList.getLookup("inEventSeries", withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup=self.eventSeriesList.getLookup("acronym",withDuplicates=True)
        
        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents=self.seriesLookup[seriesAcronym]
                if self.debug:
                    print(f"{seriesAcronym}:{len(seriesEvents):4d}" )
            else:
                if self.debug:
                    print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print ("%d events/%d eventSeries -> %d linked" % (len(self.eventList.getList()),len(self.eventSeriesList.getList()),len(self.seriesLookup)))


    def generateCSV(self,pageTitles,filename,filepath= "%s/.ptp/csvs/" % (expanduser("~"))):
        """
        Generate a csv with the given pageTitles
        Args:
            pageTitles(list):List of pageTitles to generate CSV from
            filename(str):CSV file name
            filepath(str):filepath to create csv. Default: ~/.ptp/csvs/
        """
        wikiFileMananger = self.eventList.wikiFileManger
        LoD = wikiFileMananger.exportWikiSonToLOD(pageTitles, 'Event')
        if self.debug:
            print(pageTitles)
            print(LoD)

        savepath = filepath + filename
        hf.ensureDirectoryExists(savepath)
        CSV.storeToCSVFile(LoD, savepath)
        return savepath

    def getEventCsv(self,eventTitle):
        """
        Gives a csv file for the eventTitle
        """
        return self.generateCSV([eventTitle],eventTitle)

    def getEventSeriesCsv(self,eventSeriesTitle):
        """
        Gives a csv file for all the events the given eventSeriesTitle
        """
        eventsInSeries = self.getEventsInSeries(eventSeriesTitle)
        pageTitles = []
        for event in eventsInSeries:
            if hasattr(event, 'pageTitle'):
                pageTitles.append(event.pageTitle)
        return self.generateCSV(pageTitles,eventSeriesTitle)

    def getEventsInSeries(self,seriesAcronym):
        """
        Return all the events in a given series.
        """
        if seriesAcronym in self.seriesAcronymLookup:
            seriesEvents = self.seriesLookup[seriesAcronym]
            if self.debug:
                print(f"{seriesAcronym}:{len(seriesEvents):4d}")
        else:
            if self.debug:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
            return None
        return seriesEvents
