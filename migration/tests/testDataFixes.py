'''
Created on 2021-04-02

@author: wf
'''
import unittest
from os import path

from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.fixer import PageFixer
from openresearch.event import Event
from lodstorage.jsonable import Types

class TestDataFixes(unittest.TestCase):

    def setUp(self):
        self.debug=False
        pass

    def tearDown(self):
        pass

    def testDateParser(self):
        '''
        test the date parser used to convert dates in issue 71
        '''
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',hf.parseDate(date))


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

    def testDictionaryLoad(self):
        """
        test for loading the lookup Dictionary
        """
        lookup_dict=hf.loadDictionary
        self.assertIsNotNone(lookup_dict)


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