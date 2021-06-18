'''
Created on 2021-04-15

@author: mk
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.issue170_curation import CurationQualityChecker
from tests.corpus import Corpus
from openresearch.event import Event,EventList
from collections import Counter


class TestIssue236(unittest.TestCase):
    '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/236

        tests for self updating and fixing of events for CSV round trip issue
    '''

    def setUp(self):
        self.debug = False
        pass

    def tearDown(self):
        pass

    def testUpdateEntity(self):
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