'''
Created on 2021-04-02

@author: wf
'''
import unittest
from migrate.issue152 import AcceptanceRateFixer
import getpass

class TestIssue152(unittest.TestCase):
    '''
    test for fixing Acceptance Rate Not calculated
    https://github.com/SmartDataAnalytics/OpenResearch/issues/152
    '''

    def setUp(self):
        self.debug=False
        pass
    
    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];


    def tearDown(self):
        pass


    def testIssue152(self):
        '''
        test Issue 152
        '''
        fixer=AcceptanceRateFixer()
        pages=fixer.getAllPages()
        self.assertTrue(len(pages>18000))


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()