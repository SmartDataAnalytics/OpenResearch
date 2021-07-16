'''
Created on 12.07.2021

@author: wf
'''
import unittest
from ormigrate.issue119_ordinal import OrdinalFixer
from tests.corpusfortesting import CorpusForTesting as Corpus
from ormigrate.toolbox import HelperFunctions as hf
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.fixer import PageFixerManager
from ormigrate.toolbox import Profiler

class TestOrdinalFixer(unittest.TestCase):
    '''
    test the ordinal fixer
    '''

    def setUp(self):
        self.testAll=True
        pass


    def tearDown(self):
        pass
    
    def testDictionaryLoad(self):
        """
        test for loading the lookup Dictionary
        """
        lookup_dict=hf.loadDictionary()
        self.assertIsNotNone(lookup_dict)
        ord61=lookup_dict.getToken("61st")
        self.assertEqual("enum",ord61["type"])
        self.assertEqual(61,ord61["value"])
        

    def testOrdinalFixer(self):
        '''
        test the ordinal Fixer on pageTitle examples
        '''
        pageLists=PageFixerToolbox.getPageTitleLists("IEAI 2021","AIAT 2021",testAll=self.testAll)
        for pageList in pageLists:
            pageCount="all" if pageList is None else len(pageList)
            profile=Profiler(f"testing ordinals for {pageCount} pages")
            args=PageFixerToolbox.getArgs(pageList,["--stats"],debug=self.debug)
            pageFixerManager=PageFixerManager.runCmdLine([OrdinalFixer],args)
            profile.time()
            counters=pageFixerManager.getRatingCounters()
            painCounter=counters["pain"]
            debug=self.debug
            if debug:
                print (painCounter)

    def testOrdinalFixerExamples(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/119
        '''
        wikiFileManager=Corpus.getWikiFileManager()
        fixer=OrdinalFixer(wikiFileManager)
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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()