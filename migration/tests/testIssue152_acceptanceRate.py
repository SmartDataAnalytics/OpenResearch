'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue152_acceptancerate import AcceptanceRateFixer
from tests.pagefixtoolbox import PageFixerToolbox

class TestIssue152AcceptanceRate(unittest.TestCase):
    '''
    tests for Issue 152 Acceptance Rate Not calculated 
    '''

    def setUp(self):
        self.debug=False
        self.testAll=True
        pass


    def tearDown(self):
        pass


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
        fixer=PageFixerToolbox.getPageFixer(AcceptanceRateFixer)
        for event in eventRecords:
            painRating =fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[1,3,5,7])
        
    def testIssue152Rating(self):
        '''
        tries rating https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        pageTitleLists=PageFixerToolbox.getPageTitleLists("BTU 2009","FCT 1993",testAll=self.testAll)
        for pageTitleList in pageTitleLists:
            counters=PageFixerToolbox.getRatingCounters(self, pageTitleList, AcceptanceRateFixer,debug=self.debug)
            painCounter=counters["pain"]
            # TODO - make sure the pain counters work if calculated from the wikiFiles (propertyMapping!)
            if pageTitleList is None:
                self.assertTrue(painCounter[5]>1000)
            else:
                self.assertEqual(2,painCounter[3])

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()