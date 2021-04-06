'''
Created on 2021-04-06

@author: wf
'''
import unittest
from openresearch.event import Event
from lodstorage.jsonable import JSONAble, Types

class TestEvent(unittest.TestCase):


    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testEvent(self):
        '''
        try out 
        '''
        types=Types("Event")
        samples=Event.getSamples()
        types.getTypes("events", samples, 1)
        print(types.typeMap)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()