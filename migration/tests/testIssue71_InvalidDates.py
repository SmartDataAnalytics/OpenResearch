'''
Created on 15.07.2021

@author: wf
'''
import unittest
from ormigrate.issue71_date import DateFixer
from tests.pagefixtoolbox import PageFixerToolbox

class TestInvalidDatesFixer(unittest.TestCase):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/71
    '''

    def setUp(self):
        self.testAll=True
        pass


    def tearDown(self):
        pass

    def testDateParser(self):
        '''
        test the date parser used to convert dates in issue 71
        '''
        dateFixer=PageFixerToolbox.getPageFixer(DateFixer)
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',dateFixer.parseDate(date))
            
    def testIssue71Examples(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
        # TODO add invalid dates that are not properly formatted examples
        eventRecords = [{'startDate': '20 Feb, 2020', 'endDate': '20 Feb, 2020'},
                        {'startDate': None, 'endDate': None},
                        {'startDate': '20 Feb, 2020', 'endDate': None},
                        {'startDate': None, 'endDate': '20 Feb, 2020'},
                        ]
        expectedPainRatings=[1, 5, 3, 7]
        expectedStartDates=['2020/02/20', None, '2020/02/20', None]
        expectedEndDates=['2020/02/20', None, None, '2020/02/20']
        painRatings=[]
        fixedStartDates=[]
        fixedEndDates=[]
        fixer=PageFixerToolbox.getPageFixer(DateFixer)
        for event in eventRecords:
            painRating = fixer.getRating(event)
            event,_err = fixer.fixEventRecord(event, ['startDate', 'endDate'])
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
            fixedStartDates.append(event['startDate'])
            fixedEndDates.append(event['endDate'])
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedStartDates, fixedStartDates)
        self.assertEqual(expectedEndDates, fixedEndDates)
            
    def testIssue71Rating(self):
        '''
        test the rating handling for the data Fixer
        '''
        pageTitleLists=PageFixerToolbox.getPageTitleLists("SCA 2020",testAll=self.testAll)
        for pageTitleList in pageTitleLists:
            counters=PageFixerToolbox.getRatingCounters(self, pageTitleList, DateFixer, debug=self.debug)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[2]>1500)
            else:
                self.assertEqual(2,painCounter[1])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()