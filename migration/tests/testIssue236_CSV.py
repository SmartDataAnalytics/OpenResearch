'''
Created on 2021-04-15

@author: mk
'''
import unittest

from lodstorage.storageconfig import StorageConfig

from tests.corpusfortesting import CorpusForTesting as Corpus
import csv
from datasources.openresearch import OREvent,OREventManager, OREventSeriesManager

class TestIssue236(unittest.TestCase):
    '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/236

        tests for self updating and fixing of events for CSV round trip issue
        ToDo: Once ConferenceCorpus has the csv functionality migrate these tests
    '''
    
    @classmethod
    def setUpClass(cls):
        '''
        setup for all test functions in this class
        '''
        cls.debug=False
        #cls.eventCorpus=Corpus.getEventCorpusFromWikiText()
        cls.eventCorpus=Corpus.getEventCorpusFromWikiAPI(debug=cls.debug)
        pass
    
    def setup(self):
        '''
        setup per single test
        '''
        self.debug = TestIssue236.debug
        self.eventCorpus=TestIssue236.eventCorpus
  
    def tearDown(self):
        pass


    def testGetEventLinkedToSeries(self):
        '''
        get getting the events in a certain series
        e.g. 3DUI
        '''
        #self.debug=True
        eventsLinked=self.eventCorpus.eventManager.getEventsInSeries('3DUI')
        for event in eventsLinked:
            self.assertEqual("3DUI",event.inEventSeries)
            if self.debug:
                print(event)
        
        self.assertGreaterEqual(len(eventsLinked), 2)
        
    def checkCSV(self,csvFilePath,minRows=1):
        '''
        check the given CSV file
        '''
        rows=0
        with open (csvFilePath) as csvFile:
            csvReader=csv.reader(csvFile)
            for row in csvReader:
                rows+=1
                if self.debug:
                    print (row)
        self.assertTrue(rows>=minRows)

    def testCsvGeneration(self):
        """
        Test the module for csv generation module in Event Corpus
        """
        eventCSVFile = self.eventCorpus.getEventCsv('3DUI 2020')
        self.checkCSV(eventCSVFile)
        eventSeriesCSVFile= self.eventCorpus.getEventSeriesCsv('3DUI')
        self.checkCSV(eventSeriesCSVFile)

    def testUpdateEntity(self):
        """
        tests updating an event from EventList
        """
        eventList = OREventManager()
        eventSamples=OREvent.getSamples()
        eventList.fromLoD(eventSamples)
        eventDict1=eventSamples[0]
        eventDict1['testAttr']='test'
        event= OREvent()
        event.fromDict(eventDict1)
        eventList.smwHandler.updateEntity(event)
        eventDict2 = eventSamples[-1]
        event2 = OREvent()
        event2.fromDict(eventDict2)
        eventList.smwHandler.updateEntity(event2)
        updatedList = eventList.getList()
        self.assertEqual(updatedList[0].testAttr,'test')
        self.assertEqual(len(updatedList),len(eventSamples))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()