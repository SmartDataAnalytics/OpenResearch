'''
Created on 2021-04-15

@author: mk
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from openresearch.eventcorpus import EventCorpus
from openresearch.event import Event,EventList, EventSeriesList


class TestIssue236(unittest.TestCase):
    '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/236

        tests for self updating and fixing of events for CSV round trip issue
    '''

    def setUp(self):
        self.debug = False
        self.wikiId='orclone'
        pass

    def tearDown(self):
        pass


    def testGetEventSeries(self):
        if hf.inPublicCI():return
        eventCorpus = EventCorpus(debug=self.debug)
        eventCorpus.fromWikiSonBackupFiles(wikiId=self.wikiId)
        eventsLinked=eventCorpus.getEventsInSeries('3DUI')
        self.assertGreaterEqual(len(eventsLinked), 2)

    def testDictConversion(self):
        if hf.inPublicCI(): return
        eventList2 = EventList()
        eventList2.fromWikiSonBackupFiles('Event', wikiId=self.wikiId, listOfItems=['3DUI 2020', '3DUI 2016'])
        self.assertGreaterEqual(len(eventList2.getList()), 2)


    def testFromBackupFile(self):
        if hf.inPublicCI():return
        eventSeriesList=EventSeriesList()
        eventSeriesList.fromWikiSonBackupFiles('Event series',wikiId=self.wikiId)
        self.assertGreater(len(eventSeriesList.getList()), 100)
        eventList= EventList()
        eventList.fromWikiSonBackupFiles('Event',wikiId='orcp')
        self.assertGreater(len(eventList.getList()),8000)
        eventList2= EventList()
        eventList2.fromWikiSonBackupFiles('Event',wikiId='orcp',listOfItems=['3DUI 2020','3DUI 2016'])
        self.assertGreaterEqual(len(eventList2.getList()), 2)

    def testUpdateEntity(self):
        if hf.inPublicCI(): return
        eventList = EventList()
        eventSamples=Event.getSamples()
        eventSamples.pop()
        eventList.fromLoD(eventSamples)
        eventSamples= Event.getSamples()
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