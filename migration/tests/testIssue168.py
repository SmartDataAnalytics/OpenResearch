'''
Created on 2021-04-13

@author: wf
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from openresearch.eventcorpus import EventCorpus
from openresearch.event import Event
from collections import Counter


class TestIssue168(unittest.TestCase):
    '''
    add Rating Callback option #168
    '''


    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass
    
    def getEventCorpus(self,debug=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventCorpus=EventCorpus(debug=debug)
        eventCorpus.fromWikiUser(wikiUser)
        return eventCorpus


    def testEventsWithSeries(self):
        eventCorpus=self.getEventCorpus(debug=self.debug)
        

    def testRatingCallback(self):
        '''
        test the rating call back
        '''
        eventCorpus=self.getEventCorpus(debug=self.debug)
        lod=eventCorpus.eventList.getRatedLod(Event.rateMigration)
        counter=Counter()
        for record in lod:
            counter[record["acronym"]]+=1
        print(counter.most_common(50))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()