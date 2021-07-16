'''
Created on 2021-07-14

@author: wf
'''
import unittest
from tests.corpusfortesting import CorpusForTesting as Corpus
from ormigrate.toolbox import Profiler

class TestEventCorpus(unittest.TestCase):
    '''
    test handling the event corpus
    '''

    def setUp(self):
        self.debug = False
        self.profile=True
        pass

    def tearDown(self):
        pass
    
    def checkEventCorpus(self,eventCorpus):
        '''
        check the given eventCorpus
        '''
        listOfEvents=eventCorpus.eventList.getList()
        withSeries=0
        for event in listOfEvents:
            self.assertTrue(hasattr(event, 'lastEditor'))
            if hasattr(event,'inEventSeries'): withSeries+=1
        if self.debug:
            print(f"inEventseries: {withSeries}")
        self.assertTrue(withSeries>4500)

    def testEventCorpusFromWikiUser(self):
        '''
        test the event corpus
        '''
        profile=Profiler("getting EventCorpus from WikiUser")
        eventCorpus=Corpus.getEventCorpusFromWikiAPI(debug=self.debug, force=True)
        profile.time()
        self.checkEventCorpus(eventCorpus)
        
        
    def testEventCorpusFromWikiUserCache(self):
        """
        test the Event Corpus from the wikiUser(API) cache.
        """
        debug = False
        #TODO: Only test when json is available. Expects to run less than 1 sec
        if Corpus.hasCache():
            profile=Profiler(f"getting EventCorpus for {Corpus.wikiId} from WikiUser Cache",self.profile)
            eventCorpus=Corpus.getEventCorpusFromWikiAPI(debug=debug, force=False)
            profile.time()
            self.checkEventCorpus(eventCorpus)
        

    def testEventCorpusFromWikiFileManager(self):
        """
        test the Event Corpus from the wiki file manager(wikiFiles).
        """
        profile=Profiler(f"getting EventCorpus from wikiText files for {Corpus.wikiId}")
        eventCorpus = Corpus.getEventCorpusFromWikiText(debug=self.debug)
        profile.time()
        self.checkEventCorpus(eventCorpus)

    def testMatchingSetsForEventCorpus(self):
        """
        test the different sets of Event Corpus and check the similarities between them
        """
        pass

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()