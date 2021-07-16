'''
Created on 2021-07-13

@author: wf
'''
import unittest
from ormigrate.fixer import PageFixerManager
from ormigrate.issue150_nullvalue import NullValueFixer
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.toolbox import Profiler

class TestNullValueFixer(unittest.TestCase):
    '''
    Test the fixer for Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def setUp(self):
        self.debug=False
        self.testAll=True
        pass

    def tearDown(self):
        pass

    def testNullValueFixer(self):
        '''
        test fixing https://confident.dbis.rwth-aachen.de/or/index.php?title=ECIR
        '''
        pageLists=PageFixerToolbox.getPageTitleLists("ECIR 2019","ECIR 2018","ECIR 2017","ECIR 2009",testAll=self.testAll)
        for pageList in pageLists:
            pageCount="all" if pageList is None else len(pageList)
            profile=Profiler(f"testing null Values for {pageCount} pages")
            args=PageFixerToolbox.getArgs(pageList,["--stats"],debug=self.debug)
            pageFixerManager=PageFixerManager.runCmdLine([NullValueFixer],args)
            profile.time()
            counters=pageFixerManager.getRatingCounters()
            painCounter=counters["pain"]
            debug=self.debug
            if debug:
                print (painCounter)
            if pageList is not None:
                self.assertEqual(0,len(pageFixerManager.errors))
                self.assertEqual(4,len(pageFixerManager.ratings))
                self.assertEqual(1,painCounter[1])
            else:
                self.assertTrue(painCounter[5]>350)
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()