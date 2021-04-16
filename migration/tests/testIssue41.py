import unittest
from ormigrate.issue41 import AcronymLengthFixer


class TestIssue41(unittest.TestCase):
    '''
    test issue 41 fixer
    
    https://github.com/SmartDataAnalytics/OpenResearch/issues/41
    Fix Acronym length histogram outliers #41
    
    TODO:
    https://github.com/SmartDataAnalytics/OpenResearch/issues/85
    Check pages where Acronym is different from PAGENAME 
    '''

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
            print (rating)
            self.assertTrue(rating.pain == painRating)