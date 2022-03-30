'''
Created on 2021-11-17

@author: th
'''
from ormigrate.issue211_year import YearFixer
from tests.pagefixtoolbox import PageFixerTest

class TestYearFixer(PageFixerTest):
    '''
    tests fixing and rating of issue #211 (year property)
    https://github.com/SmartDataAnalytics/OpenResearch/issues/211
    '''

    def setUp(self, **kwargs):
        PageFixerTest.setUp(self)
        self.pageFixerClass=YearFixer
        self.eventRecords=[
            {
                "expected":{"year":"2020"},
                "raw":{"year":"2020"},
                "rating":0
            },
            {
                "expected": {"year": 2020},
                "raw": {"year": 2020},
                "rating":0
            },
            {
                "expected": {"year": None},
                "raw": {"year": "1404"},  # unrealistic year for a conference in or
                "rating":5
            },
            {
                "expected": {"year": "2020", "startDate":"2020-01-01"},
                "raw": {"year": None, "startDate":"2020-01-01"},
                "rating": 3
            },
            {
                "expected": {"year": None},
                "raw": {"year": None},
                "rating": 8
            },
            {
                "expected": {"year": "2020", "endDate": "2020-01-01"},
                "raw": {"year": None, "endDate": "2020-01-01"},
                "rating": 3
            }
        ]

    def test_fix(self):
        """
        tests fixing the year property
        """
        fixer = self.getPageFixer()
        for record in self.eventRecords:
            entity = self.getEntityRatingFromDict(record["raw"])
            fixer.fix(entity)
            self.assertDictEqual(record["expected"], self.getRecordOfEntity(entity))

    def test_rate(self):
        """
        tests rating the year property
        """
        fixer=self.getPageFixer()
        for record in self.eventRecords:
            entity=self.getEntityRatingFromDict(record["raw"])
            rating=fixer.rate(entity)
            self.assertEqual(record["rating"], rating.pain)
