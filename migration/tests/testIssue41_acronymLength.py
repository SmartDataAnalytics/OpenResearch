import unittest
from ormigrate.fixer import PageFixerManager
from ormigrate.issue41_acronym import AcronymLengthFixer
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.toolbox import Profiler

class TestIssue41(unittest.TestCase):
    '''
    test issue 41 fixer
    
    https://github.com/SmartDataAnalytics/OpenResearch/issues/41
    Fix Acronym length histogram outliers #41
    
    TODO:
    https://github.com/SmartDataAnalytics/OpenResearch/issues/85
    Check pages where Acronym is different from PAGENAME 
    '''

    def setUp(self) -> None:
        '''
        set up the test environment
        '''
        self.debug=False
        self.testAll=hf.inPublicCI()
        self.testAll=True
              
    def testPagesAcronym(self):
        '''
        test pages acronym fixing
        '''
        pageLists=PageFixerToolbox.getPageTitleLists("LICS 2008","FSE 1997",testAll=self.testAll)
        for pageList in pageLists:
            pageCount="all" if pageList is None else len(pageList)
            profile=Profiler(f"testing acronym length for {pageCount} pages")
            args=PageFixerToolbox.getArgs(pageList,["--stats"],debug=self.debug)
            pageFixerManager=PageFixerManager.runCmdLine([AcronymLengthFixer],args)     
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
         
    def testgetPainRating(self):
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