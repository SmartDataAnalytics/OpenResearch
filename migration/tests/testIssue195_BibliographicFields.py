'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue195_biblographic import BiblographicFieldFixer

class Test(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testBibliograpicFieldFixer(self):
        '''
            test for fixing invalid dates
            
        '''
        eventRecords = [{'has Proceedings Bibliography': 'test', 'has Bibliography': 'test'},
                        {'startDate': '20 Feb, 2020', 'endDate': '20 Feb, 2020'},
                        {'Ordinal': 2},
                        {'has Bibliography':'test'}
                        ]
        painRatings=[]
        fixer=BiblographicFieldFixer
        for event in eventRecords:
            painRating = fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[7,1,1,5])


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()