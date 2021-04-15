'''
Created on 2021-04-13

@author: wf
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from openresearch.event import Event,EventList
from collections import Counter

class TestIssue168(unittest.TestCase):
    '''
    add Rating Callback option #168
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testRatingCallback(self):
        '''
        test the rating call back
        '''
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventList=EventList()
        eventList.fromCache(wikiUser)
        print (len(eventList.getList()))
        lod=eventList.getRatedLod(Event.rateMigration)
        counter=Counter()
        for record in lod:
            counter[record["acronym length"]]+=1
        print(counter.most_common(50))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()