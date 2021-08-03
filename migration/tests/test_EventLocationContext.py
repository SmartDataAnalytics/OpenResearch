import os

from ormigrate.EventLocationHandler import EventLocationHandler
from unittest import TestCase

from ormigrate.toolbox import Profiler
from tests.corpusfortesting import CorpusForTesting


class TestEventLocationHandler(TestCase):
    '''
    test the event Location context
    '''
    def setUp(self) -> None:
        self.profile = True
        home = os.path.expanduser("~")
        targetWikiTextPath = f"{home}/.or/generated/Location"
        self.wikiFileManager = CorpusForTesting.getWikiFileManager()
        self.wikiFileManager.targetPath=targetWikiTextPath
        self.eventDataSource=CorpusForTesting.getEventDataSourceFromWikiText()
        self.eventLocationContext=EventLocationHandler(wikiFileManager=self.wikiFileManager)

    def test_generateLocationPages(self):
        """
        tests if the location page is generated correctly
        """
        profile=Profiler("Generate country location pages",self.profile)
        countries=self.eventLocationContext.locationContext.countries[:10]
        self.eventLocationContext.generateLocationPages(countries, overwrite=True)
        profile.time()
        # ToDo: test if country pages are generated correctly

    def test_generateORLocationPages(self):
        """
        Tests if the location pages are correctly generated for openresearch
        Difference to LocationContext is the reduced amount of cities that are generated
        Note: Not running in CI since it generates a lot of pages and uses functionalities which are test in the other tests
        """
        profile = Profiler("Generate OPENRESEARCH location pages (Limited to 100 events)", self.profile)
        self.eventLocationContext.generateORLocationPages(self.eventDataSource.eventManager.events[:100], overwrite=True)
        profile.time()
        # ToDo: test if generated correctly

    def test__add_page_title_to_labels(self):
        '''
        tests if the generated pageTitles are correctly assigned as location labels
        '''
        profile = Profiler("Test adding openresearch location pageTitles to location labels", self.profile)
        expectedLabel="US/CA"
        res=self.eventLocationContext.locationContext.getRegions(expectedLabel)
        self.assertTrue(len(res)==1)
        ca=res[0]
        self.assertEqual(ca.wikidataid,"Q99")
        profile.time()


    def test_getFieldCounter(self):
        '''
        test the correct counting field values of LoDs
        '''
        profile = Profiler("Testing the correct counting field values of LoDs", self.profile)
        lod=[
            {"test":"First"},
            {"Test": "Second"},
            {"test": "Second"},
            {"Test": "Third"},
            {"test": "Third"},
            {"test": "Third"},
        ]
        counterList=EventLocationHandler.getFieldCounter(lod, 'Test', 'test')
        self.assertEqual(counterList.get("First"), 1)
        self.assertEqual(counterList.get("Second"), 2)
        self.assertEqual(counterList.get("Third"), 3)
        profile.time()