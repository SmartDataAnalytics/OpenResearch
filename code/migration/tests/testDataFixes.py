'''
Created on 2021-04-02

@author: wf
'''
import unittest
import io
from os import path
from migrate.issue152 import AcceptanceRateFixer
from migrate.issue119 import OrdinalFixer
from migrate.issue71 import DateFixer

from migrate.toolbox import HelperFunctions
from migrate.fixer import PageFixer
from openresearch.event import Event
from lodstorage.jsonable import JSONAble, Types
import getpass

class TestDataFixes(unittest.TestCase):

    def setUp(self):
        self.debug=False
        pass
    
    def inPublicCI(self):
        '''
        are we running in a public Continuous Integration Environment?
        '''
        return getpass.getuser() in [ "travis", "runner" ];


    def tearDown(self):
        pass

    def testDateParser(self):
        '''
        test the date parser used to convert dates in issue 71
        '''
        sampledates=['2020-02-20','2020/02/20','2020.02.20','20/02/2020','02/20/2020','20.02.2020','02.20.2020','20 Feb, 2020','2020, Feb 20','2020 20 Feb','2020 Feb 20']
        for date in sampledates:
            self.assertEqual('2020/02/20',HelperFunctions.parseDate(date))

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
        pageFixer=PageFixer()
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
        pageFixer=PageFixer()
        # we'd love to test form a string
        # see https://stackoverflow.com/a/141451/1497139
        pageTitles="""Concept:Topic
Help:Topic"""
        fstdin = io.StringIO(pageTitles)
        pageTitleList=pageFixer.getAllPagesFromFile(fstdin)
        self.assertEqual(2,len(pageTitleList))

    def testFixedPath(self):
        fixer = DateFixer(debug=self.debug)
        dirname= 'Fixed'
        fixedPath = fixer.getFixedPagePath('/asd/asd/asd/test.wiki',dirname)
        self.assertTrue(fixedPath == '%s/wikibackup/%s/%s' % (path.expanduser("~"), dirname, 'test.wiki'))

    def testIssue152(self):
        '''
            test for fixing Acceptance Rate Not calculated
            https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        fixer=AcceptanceRateFixer(debug=self.debug)
        pages=fixer.getAllPages()
        if self.debug:
            print("Number of pages: ", len(pages))
        expectedPages=0 if self.inPublicCI() else 8000
        self.assertTrue(len(pages)>=expectedPages)
        events=list(fixer.getAllPageTitles4Topic("Event"))
        expectedEvents=0 if self.inPublicCI() else 5500
        if self.debug:
            print("Number of events: ", len(events))
        self.assertTrue(len(events)>=expectedEvents)
        fixer.checkAllFiles(fixer.check)
        if self.debug:
            print(fixer.result())
            print(expectedEvents)
        self.assertTrue(fixer.nosub>=0 if self.inPublicCI() else 50)
        self.assertTrue(fixer.nosub>=0 if self.inPublicCI() else 50)

    def testDictionaryLoad(self):
        """
        test for loading the lookup Dictionary
        """
        lookup_dict=HelperFunctions.loadDictionary
        self.assertIsNotNone(lookup_dict)

    def testIssue119(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/119
        '''
        fixer=OrdinalFixer(debug=self.debug)
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        lookup_dict = HelperFunctions.loadDictionary()
        fixed=fixer.convert_ordinal_to_cardinal('sample',samples[0],lookup_dict)
        fixed_dic=HelperFunctions.WikiSontoLOD(fixed)
        types.getTypes("events", fixed_dic, 1)
        self.assertTrue(types.typeMap['events']['Ordinal'] == 'int')

    def testIssue71(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
        fixer=DateFixer(debug=self.debug)
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        fixedDates=fixer.getFixedDate('sample',samples[0])
        fixedDeadlines=fixer.getFixedDate('sample',fixedDates,'deadline')
        fixed_dic=HelperFunctions.WikiSontoLOD(fixedDeadlines)
        self.assertTrue(fixed_dic[0]['Start date'] == '2020/09/27')
        self.assertTrue(fixed_dic[0]['Paper deadline'] == '2020/05/28')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()