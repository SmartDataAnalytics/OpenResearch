'''
Created on 2021-07-13

@author: wf
'''
import unittest
from ormigrate.issue150_nullvalue import NullValueFixer
from tests.pagefixtoolbox import PageFixerToolbox, PageFixerTest

class TestNullValueFixer(PageFixerTest):
    '''
    Test the fixer for Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=NullValueFixer

    def testNullValueFixer(self):
        '''
        test fixing https://confident.dbis.rwth-aachen.de/or/index.php?title=ECIR
        '''
        pageTitleLists=self.getPageTitleLists("ECIR 2019","ECIR 2018","ECIR 2017","ECIR 2009")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is not None:
                self.assertEqual(1,painCounter[1])
            else:
                self.assertTrue(painCounter[5]>350)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()