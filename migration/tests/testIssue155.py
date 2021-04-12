'''
Created on 2021-04-06

@author: wf
'''
import unittest
from openresearch.event import Event, EventList, EventSeries, EventSeriesList
from lodstorage.jsonable import  Types
from lodstorage.sql import SQLDB
from wikibot.wikipush import WikiPush
from migrate.toolbox import HelperFunctions
import time

class TestEvent(unittest.TestCase):
    '''
    test handling Event and EventSeries
    '''


    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testEventSeries(self):
        types = Types("Event Series")
        samples = EventSeries.getSamples()
        wikiSonSample = EventSeries.getSampleWikiSon()
        types.getTypes("eventseries", samples, 1)
        self.assertIsNotNone(types.typeMap)
        LOD = HelperFunctions.WikiSontoLOD(wikiSonSample[0])
        self.assertTrue(LOD[0]['Acronym'] == 'AAAI')
        # pass

    def testEvent(self):
        '''
        Tests the event object
        '''
        types=Types("Event")
        samples=Event.getSamples()
        wikiSonSample = Event.getSampleWikiSon()
        types.getTypes("events", samples, 1)
        self.assertIsNotNone(types.typeMap)
        LOD=HelperFunctions.WikiSontoLOD(wikiSonSample[0])
        self.assertTrue(LOD[0]['Acronym'] == 'ICSME 2020')
        
    def getSQLDB(self,path=None):
        if path is not None:
            sqlDB=SQLDB(path)
        else:
            sqlDB=SQLDB() # in memory DB!
        return sqlDB
    
    def getEventList(self,listOfRecords):
        self.sqlDB=self.getSQLDB()
        entityInfo=self.sqlDB.createTable(listOfRecords,'Event','pageTitle',withDrop=True,sampleRecordCount=len(listOfRecords))
        self.assertIsNotNone(entityInfo)
        self.sqlDB.store(listOfRecords,entityInfo,fixNone=True)
        if self.debug:
            print(entityInfo.createTableCmd)
        eventList=EventList()  
        eventList.fromSQLTable(self.sqlDB,entityInfo)
        return eventList
        
    def testEventSql(self):   
        '''
        test event handling with SQL
        ''' 
        listOfRecords=Event.getSamples()
        eventList=self.getEventList(listOfRecords)
        self.assertEqual(1,len(eventList.events))
  
    def testEventSeriesSql(self):
        '''
        test event series handling with SQL
        '''
        listOfRecords = EventSeries.getSamples()
        sqlDB = self.getSQLDB()
        entityInfo = sqlDB.createTable(listOfRecords, 'EventSeries', 'acronym', withDrop=True)
        self.assertIsNotNone(entityInfo)
        sqlDB.store(listOfRecords, entityInfo, fixNone=True)
        if self.debug:
            print(entityInfo.createTableCmd)
        eventSeriesList = EventSeriesList()
        eventSeriesList.fromSQLTable(sqlDB, entityInfo)
        self.assertEqual(1, len(eventSeriesList.eventSeries))
        
    def getWikiPush(self):
        wikiId = 'or'
        save=HelperFunctions.inPublicCI()
        wikiClient = HelperFunctions.getWikiClient(wikiId,save)
        wikiPush = WikiPush(fromWikiId=wikiId)
        return wikiClient,wikiPush
    
    def testWikiPush(self):
        wikiClient,wikiPush=self.getWikiPush()
        self.assertIsNotNone(wikiClient)
        
    def  testLODtoSQL(self):
        """Test if LOD is returned correctly if called from api to store to SQL"""
        wikiClient,wikiPush=self.getWikiPush()
        eventList=EventList()
        #askExtra="" if HelperFunctions.inPublicCI() else "[[Start date::>2018]][[Start date::<2019]]"
        askExtra="[[Ordinal::36]]"
        askQuery=eventList.getAskQuery(askExtra)
        if self.debug:
            print (askQuery)
        profile=self.debug
        startTime=time.time()
        lod_res = wikiPush.formatQueryResult(askQuery, wikiClient, entityName="Event")
        elapsed=time.time()-startTime
        if profile:
            print("query of %d items took %5.1f s" % (len(lod_res),elapsed))
        self.assertTrue(isinstance(lod_res, list))
        self.assertTrue(isinstance(lod_res[0], dict))
        listOfRecords = HelperFunctions.excludeFaultyEvents(lod_res)
        eventList=self.getEventList(listOfRecords)
        for event in eventList.events[:5]:
            print(event)
            print(event.toJSON())
        #self.assertTrue(len(eventList.events)>100)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()