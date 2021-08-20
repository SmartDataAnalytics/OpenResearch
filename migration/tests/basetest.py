'''
Created on 20.08.2021

@author: wf
'''
import unittest
from ormigrate.toolbox import Profiler

class ORMigrationTest(unittest.TestCase):
    '''
    Base test class for all OpenResearh migration project test cases
    '''


    def setUp(self,debug:bool=False,profile:bool=True):
        self.debug=debug
        self.profile=profile
        msg=f"test {self._testMethodName}, debug={self.debug}"
        self.profiler=Profiler(msg,profile=profile)
        pass


    def tearDown(self):
        self.profiler.time()
        pass



if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()