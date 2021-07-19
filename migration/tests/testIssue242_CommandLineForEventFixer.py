'''
Created on 2021-07-16

@author: wf
'''
import unittest
from ormigrate.issue71_date import DateFixer
from tests.pagefixtoolbox import PageFixerToolbox

class TestIssue242_CommandLineForEventFixer(unittest.TestCase):
    '''
    test https://github.com/SmartDataAnalytics/OpenResearch/issues/242
    '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testCommandLineArgs(self):
        '''
        test the command line Arguments
        '''
        #args=PageFixerToolbox.getArgs(pageTitles, moreArgs, template, verbose, debug)
        args=PageFixerToolbox.getArgs(["ECIR 2017"])
        if self.debug:
            print(args)
        self.assertTrue("--template" in args)
        pass
    
    def testListRatings(self):
        '''
        test getting a list of Ratings
        '''
        pageTitles=["ATN 2017"]
        pageFixerManager=PageFixerToolbox.runAndGetPageFixerManager(self,pageTitles,DateFixer)

        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()