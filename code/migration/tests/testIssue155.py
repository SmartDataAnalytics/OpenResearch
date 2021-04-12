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
from openresearch.dbHandler import DBHandler
import os

class TestEvent(unittest.TestCase):


    def setUp(self):
        self.debug=False
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
        
        
    def getDBPath(self):
        path = os.path.dirname(__file__) + "/../../dataset/OpenResearch.DB"
        return path
    
    def getSQLDB(self,path=None):
        if path is not None:
            sqlDB=SQLDB(path)
        else:
            sqlDB=SQLDB() # in memory DB!
        return sqlDB
        
    def testEventSql(self):   
        '''
        test event handling with SQL
        ''' 
        listOfRecords=Event.getSamples()
        sqlDB=self.getSQLDB()
        entityInfo=sqlDB.createTable(listOfRecords,'Event','acronym',withDrop=True)
        self.assertIsNotNone(entityInfo)
        sqlDB.store(listOfRecords,entityInfo,fixNone=True)
        if self.debug:
            print(entityInfo.createTableCmd)
        eventList=EventList()  
        eventList.fromSQLTable(sqlDB,entityInfo) 
        self.assertEqual(1,len(eventList.events))
  
        
    def testEventSqlWithDBHandler(self):
        path=self.getDBPath()
        listOfRecords=Event.getSamples()
        EventHandler= DBHandler('Event','acronym',path,self.debug)
        self.assertTrue(EventHandler.createTable(listOfRecords,withDrop=True))
        self.assertTrue(EventHandler.store(listOfRecords))
        if self.debug:
            print(EventHandler.getEntityInfo().createTableCmd)

    def testEventSeriesSql(self):
        path=self.getDBPath()
        listOfRecords = EventSeries.getSamples()
        EventSeriesHandler = DBHandler('EventSeries', 'acronym', path, self.debug)
        self.assertTrue(EventSeriesHandler.createTable(listOfRecords,withDrop=True))
        self.assertTrue(EventSeriesHandler.store(listOfRecords))
        if self.debug:
            print(EventSeriesHandler.getEntityInfo().createTableCmd)
           
        # pass

    def  testLODtoSQL(self):
        """Test if LOD is returned correctly if called from api to store to SQL"""
        wikiId = 'or'
        wikiClient = HelperFunctions.getWikiClient(wikiId)
        self.eventQuery = "[[IsA::Event]][[start date::>2018]][[start date::<2019]]| mainlabel = Event| ?Title = title| ?Event in series = series| ?_CDAT=creation date| ?_MDAT=modification date| ?ordinal=ordinal| ?Homepage = homepage|format=table"
        wikiPush = WikiPush(fromWikiId=wikiId)
        askQuery = "{{#ask:" + self.eventQuery + "}}"
        lod_res = wikiPush.formatQueryResult(askQuery, wikiClient, entityName="Event")
        if self.debug:
            print(lod_res)
        self.assertTrue(isinstance(lod_res, list))
        self.assertTrue(isinstance(lod_res[0], dict))
        path = self.getDBPath()
        listOfRecords = HelperFunctions.excludeFaultyEvents(lod_res)
        EventHandler = DBHandler('Event', 'acronym', path, self.debug)
        self.assertTrue(EventHandler.createTable(listOfRecords,withDrop=True,sampleRecordCount=150))
        self.assertTrue(EventHandler.store(listOfRecords,fixNone=True))
        if self.debug:
            print(EventHandler.getEntityInfo().createTableCmd)

    def testTableExists(self):
        path = self.getDBPath()
        listOfRecords = [{'test':1}]
        TestHandler = DBHandler('Test', 'test', path, self.debug)
        self.assertTrue(TestHandler.createTable(listOfRecords,withDrop=True))
        self.assertTrue(TestHandler.checkTableExists('Test'))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()