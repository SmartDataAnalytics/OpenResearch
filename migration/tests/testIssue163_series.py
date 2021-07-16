'''
Created on 2021-07-16

@author: wf
'''
import unittest


class TestIssue163(unittest.TestCase):
    '''
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIssue163(self):
        '''
        Series Fixer
        '''
        #self.debug=True
        eventRecords = [{'inEventSeries': '3DUI', 'has Bibliography': 'test'},
                        {'inEventSeries': ['test','test2'], 'endDate': '20 Feb, 2020'},
                        {'Ordinal': 2},
                        ]
        expectedPainRatings=[1, 9, 7]
        fixer=self.getSeriesFixer()
        painRatings=[]
        for eventRecord in eventRecords:
            painRating=fixer.getRating(eventRecord)
            painRatings.append(painRating.pain)
        self.assertEqual(expectedPainRatings, painRatings)
        askExtra="" if hf.inPublicCI() else "[[Creation date::>2018]][[Creation date::<2020]]"
        count=fixer.checkAll(askExtra)
        # TODO: we do not test the count here  - later we want it to be zero
        # TODO: Records obtained with fromWiki already filter the list


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()