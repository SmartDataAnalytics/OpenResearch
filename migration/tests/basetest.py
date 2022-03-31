'''
Created on 20.08.2021

@author: wf
'''
import unittest
from unittest import TestCase
from corpus.eventcorpus import EventCorpus
from corpus.lookup import CorpusLookup
from ormigrate.toolbox import Profiler, HelperFunctions
from tests.corpusfortesting import CorpusForTesting


class BaseTest(TestCase):
    '''
    base test case
    '''

    def setUp(self, debug=False, profile=True):
        '''
        setUp test environment
        '''
        TestCase.setUp(self)
        self.debug = debug
        self.profile = profile
        msg = f"test {self._testMethodName}, debug={self.debug}"
        self.profiler = Profiler(msg, profile=self.profile)
        EventCorpus.download()

    def tearDown(self):
        self.profiler.time()
        pass

    def inCI(self) -> bool:
        """
        Returns:
            True if called in CI otherwise False
        """
        return HelperFunctions.inPublicCI()


class ORMigrationTest(BaseTest):
    '''
    Base test class for all OpenResearh migration project test cases
    '''

    def setUp(self, debug:bool=False, profile:bool=True):
        '''
        setUp test environment
        '''
        super(ORMigrationTest, self).setUp(debug, profile)
        wikiFileManager=CorpusForTesting.getWikiFileManager()
        def patchEventSource(lookup: CorpusLookup):
            '''
            patches the EventManager and EventSeriesManager by adding wikiUser and WikiFileManager
            '''
            for lookupId in ["orclone", "orclone-backup", "or", "or-backup"]:
                orDataSource = lookup.getDataSource(lookupId)
                if orDataSource is not None:
                    if lookupId.endswith("-backup"):
                        orDataSource.eventManager.wikiFileManager = wikiFileManager
                        orDataSource.eventSeriesManager.wikiFileManager = wikiFileManager
                    else:
                        orDataSource.eventManager.wikiUser = wikiFileManager.wikiUser
                        orDataSource.eventSeriesManager.wikiUser = wikiFileManager.wikiUser


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()