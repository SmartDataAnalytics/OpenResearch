import unittest
from ormigrate.issue41 import AcronymLengthFixer


class TestIssue168(unittest.TestCase):
    '''
    test issue 41 fixer
    '''


    def testgetPainRating(self):
        painList = [
            (1,"IEEE 2020"),
            (1,"IEEE 2020a"),
            (6,"IEEE"),
            (6,"Title of the event used as acronym"),
            (6,None)
        ]
        eventRecord = lambda acronym: {"acronym": acronym }
        for (painRating, sample) in painList:
            self.assertTrue(AcronymLengthFixer.getRating(eventRecord(sample)) == painRating)