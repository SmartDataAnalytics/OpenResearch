'''
Created on 2021-07-15

@author: wf
'''
import unittest
from openresearch.eventcorpus import EventList,EventSeriesList
from openresearch.event import EventSeries,Event
from tests.corpusfortesting import CorpusForTesting as Corpus
from wikifile.wikiFile import WikiFile

class TestRefactoring(unittest.TestCase):
    '''
    test for refactor to cleanup redundant and misplaced code in dblpconf, OPENRESEARCH migration, geograpy and wikirender
    '''

    def setUp(self):
        pass


    def tearDown(self):
        pass


    def testWikiSonToLodPropertyMapping(self):
        '''
        test the mapping
        '''
        wikiFileManager=Corpus.getWikiFileManager()
        for entityList,entity,templateName in [
                (EventList,Event,"Event"),
                (EventSeriesList,EventSeries,"Event series")
            ]:
            #propertyLookup=entityList.getPropertyLookup()
            #print(propertyLookup)
            listOfSampleWikiSon=entity.getSampleWikiSon()
            lod=[]
            for sampleWikiSon in listOfSampleWikiSon:
                wikiFile=WikiFile(name="noname",wikiFileManager=wikiFileManager,wikiText=sampleWikiSon)
                #print(str(wikiFile))
                record=wikiFile.extract_template(templateName)
                print(record)
                lod.append(record)
            entityList.normalizeLodFromWikiSonToLod(lod)            
            print(lod)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()