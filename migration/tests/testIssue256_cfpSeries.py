'''
Created on 2021-09-28

@author: th
'''
from lodstorage.jsonable import JSONAble

from ormigrate.issue256_cfpSeries import WikiCfpIdSeriesFixer
from ormigrate.smw.rating import EntityRating
from tests.pagefixtoolbox import PageFixerTest

class TestWikiCfpSeriesId(PageFixerTest):
    '''
    test wiki CFP Series Id fixing
    '''

    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass = WikiCfpIdSeriesFixer
        self.template="Event series"
        self.fixer=self.getPageFixer(forceUpdate=True)

    def testFix(self):
        """
        tests the fixing of missing wikiCFP ids for Event series
        """
        records={"pageTitle":"VNC"}
        expectedRecords={"pageTitle":"VNC", "wikiCfpSeries": "2967"}
        rating=self.getEntityRatingFromDict(records)
        self.fixer.fix(rating)
        print(rating.getRecord())
        self.assertDictEqual(expectedRecords, self.getRecordOfEntity(rating))

    def testUriFix(self):
        """tests the fixing of the id being inside a URI"""
        records = {"pageTitle": "AAAI", "wikiCfpSeries": "http://wikicfp.com/cfp/program?id=3&s=AAAI&f=National%20Conference%20on%20Artificial%20Intelligence"}
        expectedRecords={"pageTitle": "AAAI", "wikiCfpSeries": "3"}
        rating = self.getEntityRatingFromDict(records)
        self.fixer.fix(rating)
        print(rating.getRecord())
        self.assertDictEqual(expectedRecords, self.getRecordOfEntity(rating))

    def testRate(self):
        """
        tests the rating of missing wikiCFP ids for Event series
        """
        pageTitleList = ["AMOS","VNC"]
        counters=self.getRatingCounters(pageTitleList)
        print(counters)
