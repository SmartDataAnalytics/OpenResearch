'''
Created on 2021-04-15

@author: wf
'''
import unittest
from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.issue170_curation import CurationQualityChecker
from tests.corpusfortesting import CorpusForTesting as Corpus
from collections import Counter
from tests.pagefixtoolbox import PageFixerToolbox

class TestIssue170(unittest.TestCase):
    '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/170
        
        Curation quality check
    '''
    def setUp(self):
        self.debug=False
        self.testAll=True
        pass


    def tearDown(self):
        pass


    def testCurationQualityCheck170(self):
        '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/170

        Curation quality check
        '''
        path=hf.getResourcePath() if hf.inPublicCI() else None
        userRating=CurationQualityChecker.loadUserRating(path)
        self.assertTrue("Wolfgang Fahl" in userRating)
        if self.debug:
            print(userRating)
        editingRecords= [
            {'lastEditor':'User:Wolfgang Fahl'}, 
            {'lastEditor':'User:194.95.114.12'},
            {'lastEditor':'User:John Doe'},
        ] 
        foundPains=[]
        for editingRecord in editingRecords:
            rating=CurationQualityChecker.getRating(editingRecord)
            if self.debug:
                print(f"{editingRecord}->{rating}")
            foundPains.append(rating.pain)
        #print(foundPains)
        self.assertEqual([3, 7, 7],foundPains)
        
    def testUserCount(self):
        # only needed to setup userrating yaml file
        eventCorpus=Corpus.getEventCorpusFromWikiAPI(debug=self.debug, force=True)
        userLookup=eventCorpus.eventList.getLookup("lastEditor",withDuplicates=True)
        if self.debug:
            print (f"{len(userLookup)} users")
        expected=1 if hf.inPublicCI() else 140
        print(len(userLookup))
        self.assertTrue(len(userLookup)>expected)
        counter=Counter()
        for user in userLookup.keys():
            counter[user]+=len(userLookup[user])
        # hide personal data
        #print (counter.most_common(50))
        
    def testRating(self):
        '''
        test the rating handling for the curation quality checker
        '''
        pageTitleLists=PageFixerToolbox.getPageTitleLists("SCA 2020",testAll=self.testAll)
        for pageTitleList in pageTitleLists:
            counters=PageFixerToolbox.getRatingCounters(self, pageTitleList, CurationQualityChecker)
            painCounter=counters["pain"]
            # TODO - this is not the true rating since the curator info is not available
            # from the Wiki Files - check whether a true tests makes sense with WF, AG and JF
            if pageTitleList is None:
                self.assertTrue(painCounter[10]>9000)
            else:
                self.assertEqual(1,painCounter[10])

            
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()