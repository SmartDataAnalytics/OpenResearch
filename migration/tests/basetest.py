'''
Created on 20.08.2021

@author: wf
'''
import unittest
from corpus.eventcorpus import EventCorpus
from corpus.lookup import CorpusLookup

from ormigrate.toolbox import Profiler, HelperFunctions
from tests.corpusfortesting import CorpusForTesting


class ORMigrationTest(unittest.TestCase):
    '''
    Base test class for all OpenResearh migration project test cases
    '''


    def setUp(self,debug:bool=False,profile:bool=True):
        self.debug=debug
        self.profile=profile
        msg=f"test {self._testMethodName}, debug={self.debug}"
        self.profiler=Profiler(msg,profile=profile)
        EventCorpus.download()
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
        if HelperFunctions.inPublicCI():
            lookup = CorpusLookup(lookupIds=["orclone-backup"], configure=patchEventSource, debug=debug)
            lookup.load(forceUpdate=True)
            lookup.getDataSource("orclone-backup").eventManager.store()
            lookup.getDataSource("orclone-backup").eventSeriesManager.store()


    def tearDown(self):
        self.profiler.time()
        pass




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()