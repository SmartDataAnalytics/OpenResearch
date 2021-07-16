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
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testWikiSonToLodPropertyMapping(self):
        '''
        test the mapping
        '''
        for entityListClass,entityClass in (EventList,Event),(EventSeriesList,EventSeries):
            entityList=entityListClass()
            entityList.fromSampleWikiSonLod(entityClass)
            #propertyLookup=entityList.getPropertyLookup()
            #print(propertyLookup)
            self.assertTrue(len(entityList.getList())>0)    
            for entity in entityList.getList():
                self.assertTrue(isinstance(entity,entityClass))
                if self.debug: 
                    print(entity)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()