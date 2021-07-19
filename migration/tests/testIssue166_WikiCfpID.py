'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue166_cfp import WikiCFPIDFixer
from openresearch.event import Event
from tests.pagefixtoolbox import PageFixerTest

class TestWikiCFPId(PageFixerTest):
    '''
    test wiki CFP Id fixing
    '''
    
    def setUp(self):
        PageFixerTest.setUp(self)
        self.pageFixerClass=WikiCFPIDFixer


    def testIssue166Examples(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages
        """
        fixer=self.getPageFixer()
        samplesWikiText = Event.getSampleWikiTextList()
        wikicfpid= fixer.getWikiCFPIdFromPage(samplesWikiText[1])
        self.assertIsNotNone(wikicfpid)
        self.assertEqual(wikicfpid,'3845')

        samplesDict=Event.getSamples()
        count=0
        for sample in samplesDict:
            wikiFile= fixer.fixEventFileFromWiki(sample['pageTitle'])
            if wikiFile is not None:
                count+=1
        self.assertGreaterEqual(count,1)


        fixedPage= fixer.fixPageWithDBCrosscheck('test', samplesWikiText[1], wikicfpid)
        if self.debug:
            print(fixedPage)
        fixedDict=fixedPage.extract_template('Event')
        self.assertIsNotNone(fixedDict['wikicfpId'])
        self.assertEqual(fixedDict['wikicfpId'],'3845')
        
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
                self.assertEqual(8,painCounter[5])
            else:
                self.assertTrue(painCounter[5]>2400)

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()