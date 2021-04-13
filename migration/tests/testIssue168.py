'''
Created on 2021-04-13

@author: wf
'''
import unittest
from migration.migrate.toolbox import HelperFunctions as hf
from migration.openresearch.event import Event,EventList
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
        print(counter.most_common(10))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()