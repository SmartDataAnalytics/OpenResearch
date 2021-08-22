'''
Created on 2021-08-21

@author: wf
'''
from tests.pagefixtoolbox import PageFixerTest
import unittest
from openresearch.openresearch import OpenResearch

class TestIssue228(PageFixerTest):
    '''
    Invalid entries for country
    '''
    
    def setUp(self):
        '''
        setuUp 
        '''
        super().setUp(self,debug=False)
        self.locationContext=OpenResearch.getORLocationContext()
        
    def getCountries(self):
        '''
        load countries
        '''
        cityManager=self.locationContext.cityManager
        cityManager.fromCache()
        self.citiesByIso=cityManager.getLookup("iso")
        
   
    def testIssue228(self):
        '''
        check for Invalid countries
        '''
        
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()