'''
Created on 2021-04-15

@author: mk
'''
import unittest
from tests.corpusfortesting import CorpusForTesting as Corpus
import csv
from openresearch.event import Event,EventList, EventSeriesList

class TestIssue236(unittest.TestCase):
    '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/236

        tests for self updating and fixing of events for CSV round trip issue
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


    def testGetEventSeries(self):
        '''
        get getting the events in a certain series
        e.g. 3DUI
        '''
        eventsLinked=self.eventCorpus.getEventsInSeries('3DUI')
        self.assertGreaterEqual(len(eventsLinked), 2)

    def testLimitingEventsFromBackup(self):
        '''
        tests loading of limited events from backup files.
        '''
        # TODO refactor or remove
        return
        eventList2 = EventList()
        eventList2.fromWikiSonBackupFiles('Event', wikiId=self.wikiId,backupdir=self.backupdir,listOfItems=['3DUI 2020', '3DUI 2016'])
        self.assertGreaterEqual(len(eventList2.getList()), 2)


    def testFromBackupFile(self):
        """
        Test loading of event series and eventlist from backup files.
        """
        # TODO refactor or remove
        return
        eventSeriesList=EventSeriesList()
        eventSeriesList.fromWikiSonBackupFiles('Event series',wikiId=self.wikiId,backupdir=self.backupdir)
        # self.assertGreater(len(eventSeriesList.getList()), 100)
        eventList= EventList()
        eventList.fromWikiSonBackupFiles('Event',wikiId=self.wikiId,backupdir=self.backupdir)
        self.assertGreater(len(eventList.getList()),8000)
        eventList2= EventList()
        eventList2.fromWikiSonBackupFiles('Event',wikiId=self.wikiId,backupdir=self.backupdir,listOfItems=['3DUI 2020','3DUI 2016'])
        self.assertGreaterEqual(len(eventList2.getList()), 2)
        
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
        # ToDo: eventCorpus.getEventCsv() tries to get event records from an actual wiki
        #       Either we need a docker to test this or we refactor the csv round-trip to work
        #       on the cache instead
        return
        eventCSVFile = self.eventCorpus.getEventCsv('3DUI 2020')
        self.checkCSV(eventCSVFile)
        eventSeriesCSVFile= self.eventCorpus.getEventSeriesCsv('3DUI')
        self.checkCSV(eventSeriesCSVFile)

    def testUpdateEntity(self):
        """
        tests updating an event from EventList
        """
        eventList = EventList()
        eventSamples=Event.getSamples()
        eventList.fromLoD(eventSamples)
        eventDict1=eventSamples[0]
        eventDict1['testAttr']='test'
        event= Event()
        event.fromDict(eventDict1)
        eventList.updateEntity(event)
        eventDict2 = eventSamples[-1]
        event2 = Event()
        event2.fromDict(eventDict2)
        eventList.updateEntity(event2)
        updatedList = eventList.getList()
        self.assertEqual(updatedList[0].testAttr,'test')
        self.assertEqual(len(updatedList),len(eventSamples))

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()