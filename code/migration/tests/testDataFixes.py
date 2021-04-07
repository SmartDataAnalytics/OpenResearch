'''
Created on 2021-04-02

@author: wf
'''
import unittest
import io
from migrate.issue152 import AcceptanceRateFixer
from migrate.issue119 import OrdinalFixer
from migrate.issue71 import DateFixer
from migrate.fixer import PageFixer
from openresearch.event import Event
from lodstorage.jsonable import JSONAble, Types
from migrate.Dictionary import  Dictionary
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
    
    def testNameValue(self):
        '''
        test the name value helper function
        '''
        nameValues=["|a=1","|b= a=c ","|w|b"]
        pageFixer=PageFixer()
        for i,nameValue in enumerate(nameValues):
            name,value=pageFixer.getNameValue(nameValue)
            if self.debug:
                print("%d: %s=%s" % (i,name,value))
            if i==0: self.assertEqual(name,"a") 
            if i==1: self.assertEqual(value,"a=c")
            if i==2: self.assertIsNone(value)
        

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
        

    def testIssue152(self):
        '''
            test for fixing Acceptance Rate Not calculated
            https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        fixer=AcceptanceRateFixer(debug=self.debug)
        pages=fixer.getAllPages()
        expectedPages=8000
        self.assertTrue(len(pages)>=expectedPages)
        events=list(fixer.getAllPageTitles4Topic("Event"))
        expectedEvents=5500
        self.assertTrue(len(events)>=expectedEvents)
        fixer.checkAll()
        if self.debug:
            print(fixer.result())
        self.assertTrue(fixer.nosub>=50)
        self.assertTrue(fixer.noacc>=10)

    def testIssue119(self):
        '''
            test for fixing Ordinals not a number
            https://github.com/SmartDataAnalytics/OpenResearch/issues/152
        '''
        fixer=OrdinalFixer(debug=self.debug)
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        lookup_dict = Dictionary('../../dataset/dictionary.yaml')
        fixed=fixer.convert_ordinal_to_cardinal(samples[0],lookup_dict)
        fixed_dic=Event.WikiSontoLOD(fixed)
        type_dict=types.getTypes("events", fixed_dic, 1)
        self.assertTrue(types.typeMap['events']['Ordinal'] == 'int')

    def testIssue71(self):
        '''
            test for fixing invalid dates
            https://github.com/SmartDataAnalytics/OpenResearch/issues/71
        '''
        fixer=DateFixer(debug=self.debug)
        types = Types("Event")
        samples = Event.getSampleWikiSon()
        fixed=fixer.getFixedDate('sample',samples[0])
        fixed_dic=Event.WikiSontoLOD(fixed)
        self.assertTrue(fixed_dic[0]['Start date'] == '2020/09/27')


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()