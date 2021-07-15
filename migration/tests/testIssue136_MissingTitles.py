'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue136_MissingTitle import EventSeriesTitleFixer
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.fixer import PageFixerManager

class TestIssue136(unittest.TestCase):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/136
    '''

    def setUp(self):
        self.debug=True
        pass


    def tearDown(self):
        pass


    def testIssue136(self):
        '''
        TestEventSeriesTitleFixer
        '''
        pageTitles=["CSR","DB","DELFI","EISTA","DEBS","ISS"]
        argv=PageFixerToolbox.getArgs(pageTitles,["--stats"],debug=self.debug)
        pageFixerManager=PageFixerManager.runCmdLine([EventSeriesTitleFixer],argv)
        self.assertEqual(0,len(pageFixerManager.errors))
        self.assertEqual(4,len(pageFixerManager.ratings))
     
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()