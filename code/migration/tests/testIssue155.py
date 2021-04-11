'''
Created on 2021-04-06

@author: wf
'''
import unittest
from openresearch.event import Event, EventSeries
from lodstorage.jsonable import JSONAble, Types
from lodstorage.sql import SQLDB, EntityInfo
from migrate.toolbox import HelperFunctions

class TestEvent(unittest.TestCase):


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
        
        
    def testSqlLite(self):
        listOfRecords=Event.getSamples()
        sqlDB=SQLDB(debug=self.debug,errorDebug=False) 
        entityInfo=sqlDB.createTable(listOfRecords,'Event','acronym')
        sqlDB.store(listOfRecords,entityInfo,executeMany=False)
        if self.debug:
            print(entityInfo.createTableCmd)
           
        # pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()