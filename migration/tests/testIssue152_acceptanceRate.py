'''
Created on 2021-07-16

@author: wf
'''
import unittest


class TestIssue153AcceptanceRate(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIssue152(self):
        '''
            test for fixing Acceptance Rate Not calculated
            https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        eventRecords= [{'submittedPapers':'test', 'acceptedPapers':'test'},
                       {'submittedPapers': None, 'acceptedPapers':None},
                       {'submittedPapers':'test', 'acceptedPapers':None},
                       {'submittedPapers':None, 'acceptedPapers':'test'}]
        painRatings=[]
        fixer=self.getAcceptanceRateFixer()
        for event in eventRecords:
            painRating =fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[1,3,5,7])
        pages=fixer.getAllPages()
        if self.debug:
            print("Number of pages: ", len(pages))
        expectedPages=0 if hf.inPublicCI() else 8000
        self.assertTrue(len(pages)>=expectedPages)
        events=list(fixer.getAllPageTitles4Topic("Event"))
        expectedEvents=0 if hf.inPublicCI() else 5500
        if self.debug:
            print("Number of events: ", len(events))
        self.assertTrue(len(events)>=expectedEvents)
        fixer.checkAllFiles(fixer.check)
        if self.debug:
            print(fixer.result())
            print(expectedEvents)
        self.assertTrue(fixer.nosub>=0 if hf.inPublicCI() else 50)
        self.assertTrue(fixer.nosub>=0 if hf.inPublicCI() else 50)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()