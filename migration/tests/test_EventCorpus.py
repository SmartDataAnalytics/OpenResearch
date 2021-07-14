'''
Created on 2021-07-14

@author: wf
'''
import unittest
from tests.corpus import Corpus

class TestEventCorpus(unittest.TestCase):
    '''
    test handling the event corpus
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testEventCorpus(self):
        '''
        test the event corpus
        '''
        eventCorpus=Corpus.getEventCorpus(debug=self.debug,force=True)
        listOfEvents=eventCorpus.eventList.getList()
        withSeries=0
        for event in listOfEvents:
            self.assertTrue(hasattr(event, 'lastEditor'))
            if hasattr(event,'inEventSeries'): withSeries+=1
        if self.debug:
            print(f"inEventseries: {withSeries}")
        self.assertTrue(withSeries>4500)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()