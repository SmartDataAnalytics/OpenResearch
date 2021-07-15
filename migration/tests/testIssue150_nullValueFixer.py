'''
Created on 2021-07-13

@author: wf
'''
import unittest
from ormigrate.fixer import PageFixerManager
from ormigrate.issue150_nullvalue import NullValueFixer
from tests.pagefixtoolbox import PageFixerToolbox

class TestNullValueFixer(unittest.TestCase):
    '''
    Test the fixer for Fixer for https://github.com/SmartDataAnalytics/OpenResearch/issues/150
    '''

    def setUp(self):
        self.debug=True
        pass

    def tearDown(self):
        pass

    def testNullValueFixer(self):
        '''
        test fixing https://confident.dbis.rwth-aachen.de/or/index.php?title=ECIR
        '''
        pageTitles=["ECIR 2019","ECIR 2018","ECIR 2017","ECIR 2009"]
        argv=PageFixerToolbox.getArgs(pageTitles,["--stats"],self.debug)
        pageFixerManager=PageFixerManager.runCmdLine([NullValueFixer],argv)
        self.assertEqual(0,len(pageFixerManager.errors))
        self.assertEqual(4,len(pageFixerManager.ratings))
    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()