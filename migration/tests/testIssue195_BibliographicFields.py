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


    def testBibliograpicFieldFixer(self):
        '''
            test for fixing invalid dates
            
        '''
        eventRecords = [{'has Proceedings Bibliography': 'test', 'has Bibliography': 'test'},
                        {'startDate': '20 Feb, 2020', 'endDate': '20 Feb, 2020'},
                        {'Ordinal': 2},
                        {'has Bibliography':'test'}
                        ]
        painRatings=[]
        fixer=BiblographicFieldFixer
        for event in eventRecords:
            painRating = fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[7,1,1,5])
        
    def testRating(self):
        '''
        test the rating
        '''
        pageTitleLists=self.getPageTitleLists("SCA 2020")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[10]>9000)
            else:
                self.assertEqual(1,painCounter[10])



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()