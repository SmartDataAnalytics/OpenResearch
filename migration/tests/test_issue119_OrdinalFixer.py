'''
Created on 2021-07-12

@author: wf
'''
import unittest
from ormigrate.issue119_ordinal import OrdinalFixer
from ormigrate.toolbox import HelperFunctions as hf
from tests.pagefixtoolbox import PageFixerTest

class TestOrdinalFixer(PageFixerTest):
    '''
    test the
    fixer for Ordinal not being an integer
    https://github.com/SmartDataAnalytics/OpenResearch/issues/119
    '''
    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=OrdinalFixer
    
    def testDictionaryLoad(self):
        """
        test for loading the lookup Dictionary
        """
        lookup_dict=hf.loadDictionary()
        self.assertIsNotNone(lookup_dict)
        ord61=lookup_dict.getToken("61st")
        self.assertEqual("enum",ord61["type"])
        self.assertEqual(61,ord61["value"])
        
    def testOrdinalFixerExamples(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/119
        '''
        fixer=self.getPageFixer()
        lookup_dict = hf.loadDictionary()
        eventRecords= [{'Ordinal':2},
                       {'Ordinal':None},
                       {'Ordinal':'2nd'},
                       {'Ordinal':'test'}]
        expectedPainRatings=[1, 4, 5, 7]
        expectedOrdinals= [2, None, 2, 'test']
        painRatings = []
        ordinals=[]
        for event in eventRecords:
            painRating = fixer.getRating(event)
            res, _err = fixer.fixEventRecord(event,lookup_dict)
            ordinals.append(res['Ordinal'])
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedOrdinals, ordinals)

    def testOrdinalFixerRating(self):
        '''
        test the ordinal Fixer on pageTitle examples
        '''
        pageTitleLists=self.getPageTitleLists("ICKE 2022","IEAI 2021","AIAT 2021")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[5]>800)
            else:
                self.assertEqual(3,painCounter[5])
                

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()