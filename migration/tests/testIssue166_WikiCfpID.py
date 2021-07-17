'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue166_cfp import WikiCFPIDFixer
from openresearch.event import Event
from tests.pagefixtoolbox import PageFixerToolbox

class TestWikiCFPId(unittest.TestCase):
    '''
    test wiki CFP Id
    '''


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIssue166(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages
        """
        fixer=PageFixerToolbox.getPageFixer(WikiCFPIDFixer)
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


        count= 0
        for path, event in fixer.getAllPageTitles4Topic():
            fixedEvent=fixer.fixEventFile(path, event)
            if fixedEvent is not None:
                count +=1
        self.assertGreaterEqual(count,1000)


        fixedPage= fixer.fixPageWithDBCrosscheck('test', samplesWikiText[1], wikicfpid)
        if self.debug:
            print(fixedPage)
        fixedDict=fixedPage.extract_template('Event')
        self.assertIsNotNone(fixedDict['wikicfpId'])
        self.assertEqual(fixedDict['wikicfpId'],'3845')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()