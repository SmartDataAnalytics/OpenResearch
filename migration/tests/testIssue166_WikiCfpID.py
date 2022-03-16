'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue166_cfp import WikiCFPIDFixer
from corpus.datasources.openresearch import OREvent
from tests.pagefixtoolbox import PageFixerTest
from wikifile.wikiFile import WikiFile
from ormigrate.smw.rating import EntityRating

class TestWikiCFPId(PageFixerTest):
    '''
    test wiki CFP Id fixing
    '''
    
    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=WikiCFPIDFixer
        #self.testAll=False


    def testIssue166Examples(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages.
        Testing the fix function

        """
        fixer=self.getPageFixer()
        samplesWikiText = OREvent.getSampleWikiTextList()
        wikicfpid= fixer.getWikiCFPIdFromPage(samplesWikiText[1])
        self.assertIsNotNone(wikicfpid)
        self.assertEqual(wikicfpid,'3845')

        wikiFile = WikiFile('sampleFile',None,samplesWikiText)
        event = OREvent()
        event.wikiFile = wikiFile
        entityRating = EntityRating(event, pageTitle='Test')
        entityRating.templateName= 'Event'

        # Get Fixer
        fixer = self.getPageFixer()

        # Rate With Fixer
        fixer.rate(entityRating)
        if self.debug:
            print(entityRating)
        self.assertEqual(entityRating.pain, 5)

        # Fix With Fixer
        fixer.fix(entityRating)
        self.assertEqual(entityRating.entity.wikicfpId,"3845")


    def testIssue166Rating(self):
        """
        test the Rating function of the fixer
        """


    # TODO Change function when architecture is implemented.
    def testIssue166(self):
        '''
        test the wikicfpID handling
        '''
        pageTitleLists=self.getPageTitleLists("WebDB 2008","WebS 2008",
            "WiCOM 2008","WiCOM 2009","WiCOM 2010","WiMob 2008","WiNC 2009","WiOpt 2008")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is not None:
                self.assertEqual(8,painCounter[self.pageFixerClass.__name__][5])
            else:
                self.assertTrue(painCounter[self.pageFixerClass.__name__][5]>2400)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()