import os

from openresearch.eventcorpus import EventCorpus
from ormigrate.EventLocationContext import EventLocationContext
from wikifile.wikiFileManager import WikiFileManager
from tests.corpus import Corpus
from unittest import TestCase
from ormigrate.toolbox import HelperFunctions as hf


class TestEventLocationContext(TestCase):

    def setUp(self, wikiId='or') -> None:
        home = os.path.expanduser("~")
        wikiTextPath = f"{home}/.or/wikibackup/{wikiId}"
        targetWikiTextPath = f"{home}/.or/generated/Location"
        self.wikiFileManager = WikiFileManager(sourceWikiId=wikiId,
                                               wikiTextPath=wikiTextPath,
                                               targetWikiTextPath=targetWikiTextPath)
        eventCorpus = EventCorpus(debug=True)
        eventCorpus.fromWikiFileManager(self.wikiFileManager)

        self.eventCorpus=eventCorpus
        eventCorpus.eventList.storeToJsonFile(f"{home}/.or/Event_wikiFileBackup")

        self.eventLocationContext=EventLocationContext(wikiFileManager=self.wikiFileManager)

    def test_generateLocationPages(self):
        """
        tests if the location page is generated correctly
        """
        print("Generate country location pages")
        countries=self.eventLocationContext.locationContext.countries
        self.eventLocationContext.generateLocationPages(countries, overwrite=True)
        # ToDo: test if country pages are generated correctly

    def test_generateORLocationPages(self):
        """
        Tests if the location pages are correctly generated for openresearch
        Difference to LocationContext is the reduced amount of cities that are generated
        Note: Not running in CI since it generates a lot of pages and uses functionalities which are test in the other tests
        """
        print("Generate OPENRESEARCH location pages (Limited to 100 events)")
        self.eventLocationContext.generateORLocationPages(self.eventCorpus.eventList.events[:100], overwrite=True)
        # ToDo: test if generated correctly

    def test__add_page_title_to_labels(self):
        '''
        tests if the generated pageTitles are correctly assigned as location labels
        '''
        expectedLabel="US/CA"
        res=self.eventLocationContext.locationContext.getRegions(expectedLabel)
        self.assertTrue(len(res)==1)
        ca=res[0]
        self.assertEqual(ca.wikidataid,"Q99")


    def test_getFieldCounter(self):
        '''
        test the correct counting field values of LoDs
        '''
        lod=[
            {"test":"First"},
            {"Test": "Second"},
            {"test": "Second"},
            {"Test": "Third"},
            {"test": "Third"},
            {"test": "Third"},
        ]
        counterList=EventLocationContext.getFieldCounter(lod, 'Test', 'test')
        self.assertEqual(counterList.get("First"), 1)
        self.assertEqual(counterList.get("Second"), 2)
        self.assertEqual(counterList.get("Third"), 3)