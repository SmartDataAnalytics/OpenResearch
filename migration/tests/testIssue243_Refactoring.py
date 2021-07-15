'''
Created on 2021-07-15

@author: wf
'''
import unittest
from openresearch.eventcorpus import EventList,EventSeriesList
from openresearch.event import EventSeries,Event

class TestRefactoring(unittest.TestCase):
    '''
    test for refactor to cleanup redundant and misplaced code in dblpconf, OPENRESEARCH migration, geograpy and wikirender
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testWikiSonToLodPropertyMapping(self):
        '''
        test the mapping
        '''
        for entityList,entity in [(EventList,Event),(EventSeriesList,EventSeries)]:
            propertyLookup=entityList.getPropertyLookup()
            print(propertyLookup)
            lod=entity.getSampleWikiSon()
            print(lod)
            entityList.normalizeLodFromWikiSonToLod(lod)            
            print(lod)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()