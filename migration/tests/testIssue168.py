'''
Created on 2021-04-13

@author: wf
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from openresearch.eventcorpus import EventCorpus
from openresearch.event import Event,EventSeries
from collections import Counter


class TestIssue168(unittest.TestCase):
    '''
    add Rating Callback option #168
    '''


    def setUp(self):
        self.debug=False
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
        '''
        '''
        eventCorpus=self.getEventCorpus(debug=self.debug)
    
    def checkRatedLod(self,lod,errors):
        if len(errors)>0:
            for error in errors:
                print(error)
        self.assertEqual(0,len(errors))
        counter=Counter()
        for record in lod:
            rating=record["acronym"]
            if self.debug:
                if rating.pain>=5:
                    print (rating)
            counter[rating.pain]+=1
        print(counter.most_common(50))
        pass

    def testRatingCallback(self):
        '''
        test the rating call back
        '''
        eventCorpus=self.getEventCorpus(debug=self.debug)
        lod,errors=eventCorpus.eventList.getRatedLod(Event.rateMigration)
        self.checkRatedLod(lod, errors)
        lod,errors=eventCorpus.eventSeriesList.getRatedLod(EventSeries.rateMigration)
        self.checkRatedLod(lod, errors)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()