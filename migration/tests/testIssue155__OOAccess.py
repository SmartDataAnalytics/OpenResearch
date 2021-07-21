'''
Created on 2021-04-06

@author: wf
'''
import unittest

from lodstorage.lod import LOD

from openresearch.event import Event, EventList, EventSeries, EventSeriesList
from lodstorage.sql import SQLDB
from ormigrate.toolbox import HelperFunctions as hf, Profiler

class TestEvent(unittest.TestCase):
    '''
    test handling Event and EventSeries
    '''

    def setUp(self):
        self.debug=True


    def tearDown(self):
        pass


    def testEventSeries(self):
        '''
        test eventseries handling
        '''
        eventSeriesList=EventSeriesList()
        eventSeriesList.fromSampleWikiSonLod(EventSeries)
        self.assertTrue(len(eventSeriesList.getList())>0)
        for eventSeries in eventSeriesList.getList():
            if self.debug:
                print(eventSeries)
            self.assertTrue(isinstance(eventSeries,EventSeries))
            self.assertTrue(eventSeries.acronym is not None)
            
      
    def testEvent(self):
        '''
        Tests the event object
        '''
        eventList=EventList()
        eventList.fromSampleWikiSonLod(Event)
        self.assertTrue(len(eventList.getList())>0)
        for event in eventList.getList():
            if self.debug:
                print(event)
            self.assertTrue(isinstance(event,Event))
            self.assertTrue(event.acronym is not None)
            self.assertTrue(event.ordinal is not None)
        
    def getSQLDB(self,path=None):
        if path is not None:
            sqlDB=SQLDB(path)
        else:
            sqlDB=SQLDB() # in memory DB!
        return sqlDB
    
    def getEntityListViaSQL(self,listOfRecords,entityListClass,primaryKey='pageTitle'):
        '''
        get the list of entity for the given listOfRecord using entityListClass as the container class
        
        Args:
            listofRecords(list): the LoD 
            entityListClass(class): the class to use as the manager / container for the entity list
            primaryKey(str): the primary Key to use
            
        Returns:
            list: the list of Entities
        '''
        entityList=entityListClass()
        self.sqlDB=self.getSQLDB()
        LOD.handleListTypes(lod=listOfRecords,doFilter=False,separator=';')
        entityInfo=self.sqlDB.createTable(listOfRecords,entityList.clazz.__name__,primaryKey,withDrop=True,sampleRecordCount=len(listOfRecords))
        self.assertIsNotNone(entityInfo)
        self.sqlDB.store(listOfRecords,entityInfo,fixNone=True)
        if self.debug:
            print(entityInfo.createTableCmd)
        entityList.fromSQLTable(self.sqlDB,entityInfo)
        return entityList
    
    def getEventList(self,listOfRecords):
        eventList=self.getEntityListViaSQL(listOfRecords, EventList)
        return eventList
    
    def getEventSeriesList(self,listOfRecords):
        eventSeriesList=self.getEntityListViaSQL(listOfRecords, EventSeriesList)
        return eventSeriesList
    
    def checkEventList(self,eventList,expectedMin):
        self.assertTrue(len(eventList.events)>=expectedMin)
        
        
    def testEventSql(self):   
        '''
        test event handling with SQL
        ''' 
        listOfRecords=Event.getSamples()
        eventList=self.getEventList(listOfRecords)
        self.checkEventList(eventList, 1)
  
    def testEventSeriesSql(self):
        '''
        test event series handling with SQL
        '''
        listOfRecords = EventSeries.getSamples()
        eventSeriesList=self.getEventSeriesList(listOfRecords)
        self.assertEqual(2, len(eventSeriesList.eventSeries))
        eventSeries=eventSeriesList.eventSeries[0]
        self.assertTrue(isinstance(eventSeries,EventSeries))
        
        
    def getWikiUser(self):
        wikiuser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        return wikiuser
    
    def testLODtoSQL(self):
        """Test if LOD is returned correctly if called from api to store to SQL"""
        #ToDo: Events with list as Series property value currently lead to the fail → manual curation or filter?
        wikiuser=self.getWikiUser()
        expectedCount={"Event":100,"EventSeries":20}
        for entityListClass in EventList,EventSeriesList:
            profile=Profiler(f"testLoDtoSQL for {entityListClass.__name__}")
            entityList=entityListClass()
            entityName=entityList.getEntityName()
            entityList.debug=self.debug
            entityList.profile=self.debug
            askExtra="" if hf.inPublicCI() else "[[Creation date::>2018]][[Creation date::<2020]]"
            #askExtra="[[Ordinal::36]]"
            listOfRecords=entityList.fromWiki(wikiuser,askExtra=askExtra)
            entityList=self.getEntityListViaSQL(listOfRecords,entityListClass)
            entities=entityList.getList()
            if self.debug:
                print(f"samples for {entityName}:")
                for entity in entities[:5]:
                    print(entity)
                    print(entity.toJSON())
            self.assertTrue(len(entities)>=expectedCount[entityName])
            profile.time(f" read {len(entities)} from SQL")
            
    def testFromCache(self):
        '''
        get the eventList from the cache
        '''
        eventList=EventList()
        eventList.profile=True
        askExtra="" if hf.inPublicCI() else "[[Creation date::>2018]][[Creation date::<2020]]"
        eventList.askExtra=askExtra
        wikiuser=self.getWikiUser()
        eventList.fromCache(wikiuser)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()