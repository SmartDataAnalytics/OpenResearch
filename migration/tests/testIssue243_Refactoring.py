'''
Created on 2021-07-15

@author: wf
'''
import unittest
from datasources.openresearch import OREventList,OREventSeriesList,OREventSeries,OREvent


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
        for entityListClass,entityClass in (OREventList,OREvent),(OREventSeriesList,OREventSeries):
            entityList=entityListClass()
            entityList.fromSampleWikiSonLod(entityClass)
            self.assertTrue(len(entityList.getList())>0)    
            for entity in entityList.getList():
                self.assertTrue(isinstance(entity,entityClass))
                if self.debug: 
                    print(entity)
        pass
    
    def testPropertyLookup(self):
        '''
        test property Lookup
        '''
        for entityList in OREventSeriesList(),OREventList():
            propertyLookup=entityList.getPropertyLookup()
            if self.debug:
                print(propertyLookup)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()