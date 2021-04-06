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
        fixer=AcceptanceRateFixer(debug=self.debug)
        pages=fixer.getAllPages()
        expectedPages=0 if self.inPublicCI() else 18000
        self.assertTrue(len(pages)>=expectedPages)
        events=list(fixer.getAllPageTitles4Topic("Event"))
        expectedEvents=0 if self.inPublicCI else 10000
        self.assertTrue(len(events)>=expectedEvents)
        fixer.checkAll()
        if self.debug:
            print(fixer.result())
        if not self.inPublicCI():
            self.assertTrue(fixer.nosub>=86)
            self.assertTrue(fixer.noacc>=17)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()