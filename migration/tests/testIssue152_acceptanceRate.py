'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue152_acceptancerate import AcceptanceRateFixer
from tests.pagefixtoolbox import PageFixerTest

class TestIssue152AcceptanceRate(PageFixerTest):
    '''
    tests for Issue 152 Acceptance Rate Not calculated 
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=AcceptanceRateFixer

    def testIssue152ForRecords(self):
        '''
            test for fixing Acceptance Rate Not calculated
            https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        eventRecords= [{'submittedPapers':'test', 'acceptedPapers':'test'},
                       {'submittedPapers': None, 'acceptedPapers':None},
                       {'submittedPapers':'test', 'acceptedPapers':None},
                       {'submittedPapers':None, 'acceptedPapers':'test'}]
        painRatings=[]
        fixer=self.getPageFixer()
        for event in eventRecords:
            painRating =fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[1,3,5,7])
        
    def testIssue152Rating(self):
        '''
        tries rating https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        pageTitleLists=self.getPageTitleLists("BTU 2009","FCT 1993")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[self.pageFixerClass.__name__][3]>1000)
            else:
                self.assertEqual(2,painCounter[self.pageFixerClass.__name__][7])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()