'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue136_MissingAcronym import EventSeriesAcronymFixer
from tests.pagefixtoolbox import PageFixerTest

class TestIssue136(PageFixerTest):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/136
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=EventSeriesAcronymFixer
        self.template="Event series"

  
    def testIssue136(self):
        '''
        TestEventSeriesTitleFixer
        '''
        #self.debug=True
        pageTitleLists=self.getPageTitleLists("DB","DELFI","EISTA","DEBS","ISS")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[5]>500)
            else:
                self.assertEqual(4,painCounter[5])
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()