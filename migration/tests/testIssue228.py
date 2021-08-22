'''
Created on 2021-08-21

@author: wf
'''
from tests.pagefixtoolbox import PageFixerTest
import unittest
from ormigrate.issue228_country import CountryFixer

class TestIssue228(PageFixerTest):
    '''
    Invalid entries for country
    '''
    
    def setUp(self):
        '''
        setuUp 
        '''
        super().setUp(debug=False)
       
        pass
        
   
    def testIssue228(self):
        '''
        check for Invalid countries
        '''
        
        self.assertTrue(len(self.countriesByIso)>200)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()