'''
Created on 2021-07-14

@author: wf
'''
import unittest
from tests.corpusfortesting import CorpusForTesting as Corpus
from ormigrate.toolbox import Profiler
from lodstorage.lod import LOD
    
class MatchingSet:
    
    def __init__(self,title,list1Name,entityList1,list2Name,entityList2,keys):
        '''
        construct me
        '''
        self.title=title
        self.lod1=entityList1.getLoD()
        self.lod2=entityList2.getLoD()
        self.list1Name=list1Name
        self.list2Name=list2Name
        self.commonBy={}
        for key in keys:
            self.lodf1=self.filterKey(self.lod1,key)
            self.lodf2=self.filterKey(self.lod2,key)
            self.commonBy[key]=LOD.intersect(self.lodf1,self.lodf2,key)
            
    def filterKey(self,lod:list,key)->list:
        '''
        filter the list of dicts by the given key
        '''
        lodf=[record for record in lod if key in record and record[key] is not None]
        return lodf
            
    def showStats(self):
        for key in self.commonBy:
            commonList=self.commonBy[key]
            print(f"{self.title} {key}: {self.list1Name}: {len(self.lodf1)}/{len(self.lod1)} {self.list2Name}: {len(self.lodf2)}/{len(self.lod2)} common: {len(commonList)}")
    

class TestEventCorpus(unittest.TestCase):
    '''
    test handling the event corpus
    '''

    def setUp(self):
        self.debug = False
        self.profile=True
        self.eventCorpusAPI=None
        self.eventCorpusWikiText=None
        pass

    def tearDown(self):
        pass
    
    def checkEventCorpus(self,eventCorpus,expectedAttrs=['lastEditor','pageTitle']):
        '''
        check the given eventCorpus
        '''
        listOfEvents=eventCorpus.eventList.getList()
        withSeries=0
        for event in listOfEvents:
            for attr in expectedAttrs:
                self.assertTrue(hasattr(event, attr))
            if hasattr(event,'inEventSeries'): 
                if event.inEventSeries:
                    withSeries+=1
        if self.debug:
            print(f"inEventseries: {withSeries}")
        self.assertTrue(withSeries>4500)

    def testEventCorpusFromWikiUser(self):
        '''
        test the event corpus
        '''
        self.debug=True
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
            self.eventCorpusAPI=Corpus.getEventCorpusFromWikiAPI(debug=debug, force=False)
            profile.time()
            self.checkEventCorpus(self.eventCorpusAPI)
        

    def testEventCorpusFromWikiFileManager(self):
        """
        test the Event Corpus from the wiki file manager(wikiFiles).
        """
        profile=Profiler(f"getting EventCorpus from wikiText files for {Corpus.wikiId}")
        self.eventCorpusWikiText = Corpus.getEventCorpusFromWikiText(debug=self.debug)
        profile.time()
        self.checkEventCorpus(self.eventCorpusWikiText,['pageTitle'])    
        
    def testMatchingSetsForEventCorpus(self):
        """
        test the different sets of Event Corpus and check the similarities between them
        """
        if not Corpus.hasCache():
            return
        profile=Profiler(f"getting EventCorpora from wikiAPI and wikiText files for {Corpus.wikiId}")
        if self.eventCorpusAPI is None:
            self.eventCorpusAPI=Corpus.getEventCorpusFromWikiAPI(debug=self.debug, force=False)
        if self.eventCorpusWikiText is None:
            self.eventCorpusWikiText = Corpus.getEventCorpusFromWikiText(debug=self.debug)
        profile.time()    
        profile=Profiler(f"finding common events and series for {Corpus.wikiId}")
        keys=["acronym","pageTitle"]
        eventSet=MatchingSet("Events","api",self.eventCorpusAPI.eventList,"wikiText",self.eventCorpusWikiText.eventList,keys)
        eventSeriesSet=MatchingSet("EventSeries","api",self.eventCorpusAPI.eventSeriesList,"wikiText",self.eventCorpusWikiText.eventSeriesList,keys)
        profile.time()
        eventSet.showStats()
        eventSeriesSet.showStats()
        pass

    
if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()