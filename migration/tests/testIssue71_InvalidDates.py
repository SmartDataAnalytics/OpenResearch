'''
Created on 15.07.2021

@author: wf
'''
import unittest
from ormigrate.fixer import PageFixerManager
from ormigrate.issue71_date import DateFixer
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.toolbox import Profiler

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
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',hf.parseDate(date))
            
    def testIssue71Rating(self):
        '''
        test the rating handling for the data Fixer
        '''
        pageLists=PageFixerToolbox.getPageTitleLists("SCA 2020",testAll=self.testAll)
        for pageList in pageLists:
            pageCount="all" if pageList is None else len(pageList)
            profile=Profiler(f"testing date fixer for {pageCount} pages")
            args=PageFixerToolbox.getArgs(pageList,["--stats"],debug=self.debug)
            pageFixerManager=PageFixerManager.runCmdLine([DateFixer],args)     
            profile.time()  
            counters=pageFixerManager.getRatingCounters()
            painCounter=counters["pain"]
            debug=self.debug
            if debug:
                print (painCounter)
            if pageList is None:
                self.assertTrue(painCounter[2]>1500)
            else:
                self.assertEqual(2,painCounter[1])

        
    def testIssue71(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
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
        fixer=DateFixer()
        for event in eventRecords:
            painRating = fixer.getRating(event)
            event,err = fixer.fixEventRecord(event, ['startDate', 'endDate'])
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
            fixedStartDates.append(event['startDate'])
            fixedEndDates.append(event['endDate'])
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedStartDates, fixedStartDates)
        self.assertEqual(expectedEndDates, fixedEndDates)

    

    #    types = Types("Event")
    #   samples = Event.getSampleWikiSon()
    #    fixedDates=fixer.getFixedDateWikiFile('sample', samples[0])
    #    fixedDeadlines=fixer.getFixedDateWikiFile('sample', fixedDates, 'deadline')
    #    fixed_dic=hf.wikiSontoLOD(fixedDeadlines)
    #    self.assertTrue(fixed_dic[0]['Start date'] == '2020/09/27')
    #    self.assertTrue(fixed_dic[0]['Paper deadline'] == '2020/05/28')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()