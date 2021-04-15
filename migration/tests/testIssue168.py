'''
Created on 2021-04-13

@author: wf
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from openresearch.event import Event,EventList,EventSeriesList
from collections import Counter


class TestIssue168(unittest.TestCase):
    '''
    add Rating Callback option #168
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass
    
    def getEventsWithSeries(self,wikiUser,debug=False):
        '''
        get events with series by knitting / linking the entities together
        '''
        eventList=EventList()
        eventList.debug=debug
        eventList.fromCache(wikiUser)
        
        
        eventSeriesList=EventSeriesList()
        eventSeriesList.debug=debug
        eventSeriesList.fromCache(wikiUser)
        
        # get foreign key hashtable
        seriesLookup=eventList.getLookup("inEventSeries", withDuplicates=True)
        # get "primary" key hashtable
        seriesAcronymLookup=eventSeriesList.getLookup("acronym",withDuplicates=True)
        
        for seriesAcronym in seriesLookup.keys():
            if seriesAcronym in seriesAcronymLookup:
                seriesEvents=seriesLookup[seriesAcronym]
                print(f"{seriesAcronym}:{len(seriesEvents):4d}" )
            else:
                print(f"Event Series Acronym {seriesAcronym} lookup failed")
        if self.debug:
            print ("%d events/%d eventSeries -> %d linked" % (len(eventList.getList()),len(eventSeriesList.getList()),len(seriesLookup)))
        return eventList,eventSeriesList


    def testEventsWithSeries(self):
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventList,eventSeriesList=self.getEventsWithSeries(wikiUser,debug=True)

    def testRatingCallback(self):
        '''
        test the rating call back
        '''
        wikiUser=hf.getSMW_WikiUser(save=hf.inPublicCI())
        eventList,eventSeriesList=self.getEventsWithSeries(wikiUser)
        lod=eventList.getRatedLod(Event.rateMigration)
        counter=Counter()
        for record in lod:
            counter[record["acronym length"]]+=1
        print(counter.most_common(50))
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()