'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue195_biblographic import BiblographicFieldFixer
from tests.pagefixtoolbox import PageFixerTest

class TestBiblographicFieldFixer(PageFixerTest):
    '''
    test the BiblographicFieldFixer
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=BiblographicFieldFixer
        self.debug=True
        self.template="Event series"

        
    def testRating(self):
        '''
        test the rating
        '''
        pageTitleLists=self.getPageTitleLists("ACC")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[10]>9000)
            else:
                self.assertEqual(1,painCounter[1])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()