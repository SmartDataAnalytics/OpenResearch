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
            self.assertEqual('2020-02-20',dateFixer.parseDate(date)[0])

    def testDateParserForYear(self):
        '''
        tests the behavior of date parser when only the year is the input
        '''
        dateFixer = self.getPageFixer()
        parsedDate, errors = dateFixer.parseDate("2020")
        self.assertTrue("onlyYear" in errors)
            
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
                        {'startDate': '2011-03-22', 'endDate':'2011-03-26'},
                        ]
        expectedPainRatings=[3, 5, 5, 5,7,1]
        expectedStartDates=['2020-02-20', None, '2020-02-20', None,'2010-03-22','2011-03-22']
        expectedEndDates=['2020-02-20', None, None, '2020-02-20',None,'2011-03-26']
        expectedErrors=[0, 2, 1, 1, 1,0]
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
        return  # deactivated until ormigrate issue with ConferenceCorus data clean-up is resolved (cc is removing values that this fixer wants to rate/fix)
        #self.debug=True
        pageTitleLists=self.getPageTitleLists("IEEE TSC 2008","IJCICG 2010","IJECEE 2009")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if self.debug:
                print(painCounter)
            if pageTitleList is None:
                self.assertGreater(painCounter[self.pageFixerClass.__name__][1],500)
                self.assertGreater(painCounter[self.pageFixerClass.__name__][3], 7000)
                self.assertGreater(painCounter[self.pageFixerClass.__name__][4], 200)
                self.assertGreater(painCounter[self.pageFixerClass.__name__][5],500)
                self.assertGreater(painCounter[self.pageFixerClass.__name__][7],100)
            else:
                self.assertEqual(3,painCounter[self.pageFixerClass.__name__][7])

    def testPropertyShift(self):
        '''
        tests if only the year is given if the value is moved to the year property
        '''
        dateFixer = self.getPageFixer()
        eventRecords = [
            {
                "expected": {"year": "2020", "startDate":None},
                "raw": {"startDate": "2020"}
            },
            {
                "expected": {"year": "2020", "endDate":None},
                "raw": {"endDate": "2020"}
            },
            {
                "expected": {"year": "2020", "endDate": None, "startDate":"2020-01-05"},
                "raw": {"endDate": "2020", "startDate":"2020/01/05"}
            }
        ]
        for record in eventRecords:
            entityRating=self.getEntityRatingFromDict(record["raw"])
            dateFixer.fix(entityRating)
            self.assertDictEqual(record["expected"], self.getRecordOfEntity(entityRating))

    def testDurationVerification(self):
        """
        tests if the events have a valid duration
        """
        dateFixer = self.getPageFixer()
        eventRecords = [
            {
                "expected": {"startDate": "2020-02-01", "endDate": "2020-01-05"},
                "raw": {"startDate": "2020-02-01", "endDate": "2020-01-05"},
                "rating":4
            },
            {
                "expected": {"startDate": "2020-02-01", "endDate": "2020-02-05"},
                "raw": {"startDate": "2020-02-01", "endDate": "2020-02-05"},
                "rating":1
            },
            {
                "expected": {"startDate": "2020-02-01"},
                "raw": {"startDate": "2020-02-01"},
                "rating":5
            }
        ]
        for record in eventRecords:
            entityRating = self.getEntityRatingFromDict(record["raw"])
            dateFixer.rate(entityRating)
            self.assertEqual(record["rating"], entityRating.pain)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()