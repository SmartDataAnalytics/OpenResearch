'''
Created on 2021-04-16

@author: wf
'''
from openresearch.event import EventList,EventSeriesList
from ormigrate.toolbox import HelperFunctions as hf
from wikifile.wikiFileManager import WikiFileManager
from os.path import expanduser
from lodstorage.csv import CSV
from lodstorage.lod import LOD

class EventCorpus(object):
    '''
    Towards a gold standard event corpus  and observatory ...
    '''

    def __init__(self,debug=False,verbose=False):
        '''
        Constructor
        '''
        self.debug=debug
        self.verbose=verbose
        self._wikiFileManager=None
        self.wikiUser=None
        
    @property
    def wikiFileManager(self):
        '''
        access to wikiFileManager
        '''
        if self._wikiFileManager is not None:
            return self._wikiFileManager
        else:
            if self.wikiUser is None:
                return None
            else:
                if self.debug:
                    print(f"Creating WikiFileManager for {self.wikiUser.wikiId}")
                self._wikiFileManager = WikiFileManager(sourceWikiId=self.wikiUser.wikiId,debug=self.debug)
                return self._wikiFileManager   
            
    @wikiFileManager.setter
    def wikiFileManager(self,value):
        self._wikiFileManager=value      
        
    def linkSeriesAndEvent(self,seriesKey="Series"):
        '''
        link Series and Event using the given foreignKey
        
        Args:
            seriesKey(str): the key to be use for lookup
        '''          
        # get foreign key hashtable
        self.seriesLookup = LOD.getLookup(self.eventList.getList(),seriesKey, withDuplicates=True)
        # get "primary" key hashtable
        self.seriesAcronymLookup = LOD.getLookup(self.eventSeriesList.getList(),"acronym", withDuplicates=True)

        for seriesAcronym in self.seriesLookup.keys():
            if seriesAcronym in self.seriesAcronymLookup:
                seriesEvents=self.seriesLookup[seriesAcronym]
                if self.verbose:
                    print(f"{seriesAcronym}:{len(seriesEvents):4d}" )
            else:
                if self.debug:
                    print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print ("%d events/%d eventSeries -> %d linked" % (len(self.eventList.getList()),len(self.eventSeriesList.getList()),len(self.seriesLookup)))
                       

    def fromWikiFileManager(self,wikiFileManager):
        '''
            get events with series by knitting / linking the entities together
        '''
        self._wikiFileManager=wikiFileManager
        self.eventList = EventList()
        self.eventList.debug = self.debug
        self.eventList.fromWikiFileManager(wikiFileManager)

        self.eventSeriesList = EventSeriesList()
        self.eventSeriesList.debug = self.debug
        self.eventSeriesList.fromWikiFileManager(wikiFileManager)
        self.linkSeriesAndEvent()
        
          
    def fromWikiUser(self,wikiUser,force=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        self.wikiUser=wikiUser
        self.eventList=EventList()
        self.eventList.debug=self.debug
        if self.debug:
            self.eventList.profile=True
        self.eventList.fromCache(wikiUser,force=force)
        
        self.eventSeriesList=EventSeriesList()
        self.eventSeriesList.debug=self.debug
        if self.debug:
            self.eventSeriesList.profile=True
        self.eventSeriesList.fromCache(wikiUser,force=force)
        self.linkSeriesAndEvent("inEventSeries")
        
    def generateCSV(self,pageTitles,filename,filepath=None):
        """
        Generate a csv with the given pageTitles
        Args:
            pageTitles(list):List of pageTitles to generate CSV from
            filename(str):CSV file name
            filepath(str):filepath to create csv. Default: ~/.ptp/csvs/
        """
        if filepath is None:
            home=expanduser("~")
            filepath= f"{home}/.or/csvs/"
        lod = self.wikiFileManager.exportWikiSonToLOD(pageTitles, 'Event')
        if self.debug:
            print(pageTitles)
            print(lod)

        savepath =f"{filepath}{filename}.csv"
        hf.ensureDirectoryExists(savepath)
        CSV.storeToCSVFile(lod, savepath,withPostfix=True)
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
