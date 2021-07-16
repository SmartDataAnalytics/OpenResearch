'''
Created on 2021-07-16

@author: wf
'''
import unittest
from tests.corpusfortesting import CorpusForTesting as Corpus
from tests.pagefixtoolbox import PageFixerToolbox

class TestIssue242_CommandLineForEventFixer(unittest.TestCase):
    '''
    test https://github.com/SmartDataAnalytics/OpenResearch/issues/242
    '''

    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testCommandLineArgs(self):
        '''
        test the command line Arguments
        '''
        #args=PageFixerToolbox.getArgs(pageTitles, moreArgs, template, verbose, debug)
        args=PageFixerToolbox.getArgs(["ECIR 2017"])
        print(args)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()