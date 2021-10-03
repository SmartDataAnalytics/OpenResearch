'''
Created on 2021-04-16

@author: wf
'''
import unittest
from ormigrate.issue57_eventSeriesProvenanceFixer import EventSeriesProvenanceFixer
from tests.pagefixtoolbox import PageFixerTest

class TestIssue57(PageFixerTest):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/57
    
    Mark provenance of imported data
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=EventSeriesProvenanceFixer
        self.template="Event series"
        self.debug=False

    def testProvenanceCheck(self):
        '''
        test provenance for series handling
        '''
        self.debug=True
        pageTitleLists=self.getPageTitleLists("3DUI","ECIS")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[self.pageFixerClass.__name__][7]>900)
                self.assertTrue(painCounter[self.pageFixerClass.__name__][4]>30)
                self.assertTrue(painCounter[self.pageFixerClass.__name__][0]>20)
            else:
                self.assertEqual(2,painCounter[self.pageFixerClass.__name__][0])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()