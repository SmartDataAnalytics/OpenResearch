'''
Created on 2021-04-02

@author: wf
'''
import unittest
import io
from os import path
from ormigrate.issue152 import AcceptanceRateFixer
from ormigrate.issue119_Ordinals import OrdinalFixer
from ormigrate.issue71 import DateFixer
from ormigrate.issue163 import SeriesFixer
from ormigrate.issue166 import WikiCFPIDFixer
from ormigrate.issue195 import BiblographicFieldFixer


from ormigrate.toolbox import HelperFunctions as hf
from ormigrate.fixer import PageFixer
from openresearch.event import Event
from lodstorage.jsonable import Types

class TestDataFixes(unittest.TestCase):

    def setUp(self):
        self.debug=False
        pass

    def getWikiClient(self):
        wikiClient=hf.getWikiClient(save=hf.inPublicCI())
        return wikiClient

    def getDateFixer(self):
        fixer = DateFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()))
        return fixer

    def getOrdinalFixer(self):
        fixer = OrdinalFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()))
        return fixer

    def getPageFixer(self):
        fixer = PageFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()))
        return fixer

    def getAcceptanceRateFixer(self):
        fixer = AcceptanceRateFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()))
        return fixer

    def getBiblographicFieldFixer(self):
        fixer = BiblographicFieldFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()), debug=self.debug)
        return fixer

    def getSeriesFixer(self):
        fixer = SeriesFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()), debug=self.debug)
        return fixer

    def getWikiCFPIDFixer(self):
        fixer = WikiCFPIDFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()), debug=self.debug)
        return fixer


    def tearDown(self):
        pass

    def testDateParser(self):
        '''
        test the date parser used to convert dates in issue 71
        '''
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',hf.parseDate(date))

    '''
     @TODO       
    # def testDirectoryExists(self):
    #     ensureDirectoryExists('./test')
    #     self.assertTrue(os.path.exists('./test'))
    #     os.remove('./test')
    '''
    def testNameValue(self):
        '''
        test the name value helper function
        '''
        nameValues=["|a=1","|b= a=c ","|w|b",'|a=']
        pageFixer=self.getPageFixer()
        for i,nameValue in enumerate(nameValues):
            name,value=pageFixer.getNameValue(nameValue)
            if self.debug:
                print("%d: %s=%s" % (i,name,value))
            if i==0: self.assertEqual(name,"a") 
            if i==1: self.assertEqual(value,"a=c")
            if i==2: self.assertIsNone(value)
            if i==3: self.assertIsNone(value)
        

    def testGetAllPagesFromFile(self):
        '''
        test utility function to get pageTitles from a file e.g. stdin
        '''
        pageFixer=self.getPageFixer()
        # we'd love to test form a string
        # see https://stackoverflow.com/a/141451/1497139
        pageTitles="""Concept:Topic
Help:Topic"""
        fstdin = io.StringIO(pageTitles)
        pageTitleList=pageFixer.getAllPagesFromFile(fstdin)
        self.assertEqual(2,len(pageTitleList))

    def testFixedPath(self):
        fixer = self.getDateFixer()
        dirname= 'Fixed'
        fixedPath = fixer.getFixedPagePath('/asd/asd/asd/test.wiki',dirname)
        self.assertTrue(fixedPath == '%s/wikibackup/%s/%s' % (path.expanduser("~"), dirname, 'test.wiki'))

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

    def testIssue119(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/119
        '''
        lookup_dict = hf.loadDictionary()
        eventRecords= [{'Ordinal':2},
                       {'Ordinal':None},
                       {'Ordinal':'2nd'},
                       {'Ordinal':'test'}]
        expectedPainRatings=[1, 4, 5, 7]
        expectedOrdinals= [2, None, 2, 'test']
        painRatings = []
        ordinals=[]
        fixer=self.getOrdinalFixer()
        for event in eventRecords:
            painRating = fixer.getRating(event)
            res, err = fixer.fixEventRecord(event,lookup_dict)
            ordinals.append(res['Ordinal'])
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedOrdinals, ordinals)
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        fixed=fixer.convertOrdinaltoCardinalWikiFile('sample', samples[0], lookup_dict)
        fixed_dic=hf.wikiSontoLOD(fixed)
        types.getTypes("events", fixed_dic, 1)
        self.assertTrue(types.typeMap['events']['Ordinal'] == 'int')

    def testIssue71(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
        eventRecords = [{'startDate': '20 Feb, 2020', 'endDate': '20 Feb, 2020'},
                        {'startDate': None, 'endDate': None},
                        {'startDate': '20 Feb, 2020', 'endDate': None},
                        {'startDate': None, 'endDate': '20 Feb, 2020'},
                        ]
        expectedPainRatings=[1,3,4,5]
        expectedStartDates=['2020/02/20', None, '2020/02/20', None]
        expectedEndDates=['2020/02/20', None, None, '2020/02/20']
        painRatings=[]
        fixedStartDates=[]
        fixedEndDates=[]
        fixer=self.getDateFixer()
        for event in eventRecords:
            painRating = fixer.getRating(event)
            event,err = fixer.fixEventRecord(event, ['startDate', 'endDate'])
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
            fixedStartDates.append(event['startDate'])
            fixedEndDates.append(event['endDate'])
        self.assertEqual(expectedPainRatings,painRatings)
        self.assertEqual(expectedStartDates, fixedStartDates)
        self.assertEqual(expectedEndDates, fixedEndDates)

        types = Types("Event")
        samples = Event.getSampleWikiSon()
        fixedDates=fixer.getFixedDateWikiFile('sample', samples[0])
        fixedDeadlines=fixer.getFixedDateWikiFile('sample', fixedDates, 'deadline')
        fixed_dic=hf.wikiSontoLOD(fixedDeadlines)
        self.assertTrue(fixed_dic[0]['Start date'] == '2020/09/27')
        self.assertTrue(fixed_dic[0]['Paper deadline'] == '2020/05/28')

    def testIssue195(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
        eventRecords = [{'has Proceedings Bibliography': 'test', 'has Bibliography': 'test'},
                        {'startDate': '20 Feb, 2020', 'endDate': '20 Feb, 2020'},
                        {'Ordinal': 2},
                        {'has Bibliography':'test'}
                        ]
        painRatings=[]
        fixer=self.getBiblographicFieldFixer()
        for event in eventRecords:
            painRating = fixer.getRating(event)
            self.assertIsNotNone(painRating)
            painRatings.append(painRating.pain)
        self.assertEqual(painRatings,[7,1,1,5])

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

    def testdictToWikison(self):
        """
        Test the helper function to create wikison from a given dict
        """
        samples= Event.getSamples()
        for sample in samples:
            dic=hf.dicttoWikiSon(sample)
            self.assertEqual(type(dic),str)
            self.assertIsNotNone(dic)
            self.assertIn('acronym', dic)

    def testWikisontoDict(self):
        """
        Test the helper function to create wikison from a given dict
        """
        samples= Event.getSampleWikiSon()
        for sample in samples:
            dic=hf.wikiSontoLOD(sample)
            self.assertEqual(type(dic[0]),dict)
            self.assertIsNotNone(dic[0])
            self.assertIn('Acronym', dic[0])


    def testIssue166(self):
        """
        Tests the issue 166 for addition of WikiCFP-ID to applicable pages
        """
        if hf.inPublicCI():
            # TODO: Need the Events DB in project to run the test.
            pass
        else:
            fixer=self.getWikiCFPIDFixer()
            samples = Event.getSampleWikiSon()
            wikicfpid= fixer.getPageWithWikicfpid('test',samples[1])
            self.assertIsNotNone(wikicfpid)
            self.assertEqual(wikicfpid,'3845')
            fixedPage= fixer.fixPageWithDplp('test',samples[1],wikicfpid)
            if self.debug:
                print(fixedPage)
            fixedDict=hf.wikiSontoLOD(fixedPage)[0]
            self.assertIsNotNone(fixedDict['WikiCFP-ID'])
            self.assertEqual(fixedDict['WikiCFP-ID'],3845)


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()