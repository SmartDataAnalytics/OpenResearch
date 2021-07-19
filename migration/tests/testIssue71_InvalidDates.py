'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue71_date import DateFixer
from tests.pagefixtoolbox import PageFixerToolbox,PageFixerTest

class TestInvalidDatesFixer(PageFixerTest):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/71
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=DateFixer

    def testDateParser(self):
        '''
        test the date parser used to convert dates in issue 71
        '''
        dateFixer=self.getPageFixer()
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',dateFixer.parseDate(date)[0])
            
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
                        {'startDate': '2010/03/22', 'endDate':'2011/03/226'},
                        ]
        expectedPainRatings=[1, 5, 3, 7,7]
        expectedStartDates=['2020/02/20', None, '2020/02/20', None,'2010/03/22']
        expectedEndDates=['2020/02/20', None, None, '2020/02/20','2011/03/226']
        expectedErrors=[0, 2, 1, 1, 1]
        painRatings=[]
        errors=[]
        fixedStartDates=[]
        fixedEndDates=[]
        fixer=PageFixerToolbox.getPageFixer(DateFixer)
        for event in eventRecords:
            painRating = fixer.getRating(event)
            event,_err = fixer.fixEventRecord(event, ['startDate', 'endDate'])
            self.assertIsNotNone(painRating)
            errors.append(len(_err))
            painRatings.append(painRating.pain)
            fixedStartDates.append(event['startDate'])
            fixedEndDates.append(event['endDate'])
        self.assertEqual(expectedErrors,errors)
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedStartDates, fixedStartDates)
        self.assertEqual(expectedEndDates, fixedEndDates)
            
    def testIssue71Rating(self):
        '''
        test the rating handling for the data Fixer
        '''
        pageTitleLists=self.getPageTitleLists("IEEE TSC 2008","IJCICG 2010","IJECEE 2009")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertGreater(painCounter[7],500)
            else:
                self.assertEqual(3,painCounter[7])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()