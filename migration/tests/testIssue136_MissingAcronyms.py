'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue136_MissingAcronym import EventSeriesAcronymFixer
from tests.pagefixtoolbox import PageFixerToolbox

class TestIssue136(unittest.TestCase):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/136
    '''

    def setUp(self):
        self.debug=False
        self.testAll=True
        pass

    def tearDown(self):
        pass

    def testIssue136(self):
        '''
        TestEventSeriesTitleFixer
        '''
        pageTitleLists=PageFixerToolbox.getPageTitleLists("CSR","DB","DELFI","EISTA","DEBS","ISS",testAll=self.testAll)
        for pageTitleList in pageTitleLists:
            counters=PageFixerToolbox.getRatingCounters(self, pageTitleList, EventSeriesAcronymFixer,template="Event series",debug=self.debug)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[5]>1000)
            else:
                self.assertEqual(6,painCounter[5])
        pass

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()