'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue163_series import SeriesFixer
from tests.pagefixtoolbox import PageFixerToolbox, PageFixerTest

class TestIssue163(PageFixerTest):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/163
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=SeriesFixer
    
    def testRating(self):
        '''
        test the Rating
        '''
        #self.debug=True
        pageTitleLists=self.getPageTitleLists("IJCAI-PRICAI 2020","OPENSYM 2013",
           "WAIS 2020","WIKISYM 2011","WIKISYM 2012")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is not None:
                self.assertEqual(5,painCounter[1])
            else:
                self.assertTrue(painCounter[7]>2000)


    def testIssue163(self):
        '''
        Series Fixer
        '''
        #self.debug=True
        eventRecords = [{'inEventSeries': '3DUI', 'has Bibliography': 'test'},
                        {'inEventSeries': ['test','test2'], 'endDate': '20 Feb, 2020'},
                        {'Ordinal': 2},
                        ]
        expectedPainRatings=[1, 9, 7]
        fixer=PageFixerToolbox.getPageFixer(SeriesFixer)
        painRatings=[]
        for eventRecord in eventRecords:
            painRating=fixer.getRating(eventRecord)
            painRatings.append(painRating.pain)
        self.assertEqual(expectedPainRatings, painRatings)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()