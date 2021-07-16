'''
Created on 2021-07-15

@author: wf
'''
import unittest
from ormigrate.issue136_MissingAcronym import EventSeriesAcronymFixer
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.fixer import PageFixerManager
from ormigrate.toolbox import Profiler

class TestIssue136(unittest.TestCase):
    '''
    https://github.com/SmartDataAnalytics/OpenResearch/issues/136
    '''

    def setUp(self):
        self.debug=False
        self.testAll=True
        pass


    def tearDown(self):
        pass


    def testIssue136(self):
        '''
        TestEventSeriesTitleFixer
        '''
        pageLists=PageFixerToolbox.getPageTitleLists("CSR","DB","DELFI","EISTA","DEBS","ISS",testAll=self.testAll)
        for pageList in pageLists:
            pageCount="all" if pageList is None else len(pageList)
            profile=Profiler(f"testing missing Acronyms for {pageCount} pages")
            args=PageFixerToolbox.getArgs(pageList,["--stats"],template="Event series",debug=self.debug)
            pageFixerManager=PageFixerManager.runCmdLine([EventSeriesAcronymFixer],args)
            profile.time()
            counters=pageFixerManager.getRatingCounters()
            painCounter=counters["pain"]
            debug=self.debug
            if debug:
                print (painCounter)
            if pageList is not None:
                self.assertEqual(0,len(pageFixerManager.errors))
                self.assertEqual(6,len(pageFixerManager.ratings))
     
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()