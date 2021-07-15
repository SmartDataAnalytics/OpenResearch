import unittest
from ormigrate.fixer import PageFixer,PageFixerManager
from ormigrate.issue41_acronym import AcronymLengthFixer
from tests.pagefixtoolbox import PageFixerToolbox


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
        self.debug=False
        
    def testPagesAcronym(self):
        '''
        test pages acronym fixing
        '''
        args=PageFixerToolbox.getArgs(None,["--stats","--debug"])
        pageFixerManager=PageFixerManager.runCmdLine([AcronymLengthFixer],args)       

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