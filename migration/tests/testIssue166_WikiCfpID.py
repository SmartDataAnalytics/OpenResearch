'''
Created on 2021-07-16

@author: wf
'''
import unittest


class TestWikiCFPId(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testIssue166(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages
        """
        if hf.inPublicCI():
            # TODO: Need the Events DB in project to run the test.
            pass
        else:
            fixer=self.getWikiCFPIDFixer()
            samplesWikiSon = Event.getSampleWikiSon()
            wikicfpid= fixer.getWikiCFPIdFromPage(samplesWikiSon[1])
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


            fixedPage= fixer.fixPageWithDBCrosscheck('test', samplesWikiSon[1], wikicfpid)
            if self.debug:
                print(fixedPage)
            fixedDict=fixedPage.extract_template('Event')
            self.assertIsNotNone(fixedDict['wikicfpId'])
            self.assertEqual(fixedDict['wikicfpId'],'3845')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()