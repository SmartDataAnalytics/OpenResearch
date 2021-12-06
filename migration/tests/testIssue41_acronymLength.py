from ormigrate.issue41_acronym import AcronymLengthFixer
from tests.pagefixtoolbox import PageFixerTest

class TestIssue41(PageFixerTest):
    '''
    test issue 41 fixer
    
    https://github.com/SmartDataAnalytics/OpenResearch/issues/41
    Fix Acronym length histogram outliers #41
    
    TODO:
    https://github.com/SmartDataAnalytics/OpenResearch/issues/85
    Check pages where Acronym is different from PAGENAME 
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=AcronymLengthFixer
              
    def testPagesAcronym(self):
        '''
        test pages acronym fixing
        '''
        pageTitleLists=self.getPageTitleLists("LICS 2008","FSE 1997")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[self.pageFixerClass.__name__][2]>1500)
            else:
                self.assertEqual(2,painCounter[self.pageFixerClass.__name__][1])
         
    def testGetPainRating(self):
        painList = [
            (1,"IEEE 2020"),
            (1,"IEEE 2020a"),
            (5,"IEEE"),
            (2,"Title of the event used as acronym"),
            (6,None)
        ]
        eventRecord = lambda acronym: {"acronym": acronym }
        for (painRating, sample) in painList:
            rating=AcronymLengthFixer.getRating(eventRecord(sample))
            if self.debug:
                print (rating)
            self.assertTrue(rating.pain == painRating)