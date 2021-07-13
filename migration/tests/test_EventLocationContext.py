from unittest import TestCase
from tests.corpus import Corpus
from openresearch.eventcorpus import EventCorpus
from ormigrate.EventLocationContext import EventLocationContext


class TestEventLocationContext(TestCase):

    def setUp(self) -> None:
        self.eventCorpus=Corpus.getEventCorpus()
        self.eventLocationContext=EventLocationContext()

    def test_generateLocationPages(self):
        """
        tests if the location page is generated correctly
        """
        countries=self.eventLocationContext.locationContext.countries
        self.eventLocationContext.generateLocationPages(countries, "/tmp/wikirender", overwrite=True)
        # ToDo: test if country pages are generated correctly

    def test_generateORLocationPages(self):
        """
        Tests if the location pages are correctly generated for openresearch
        Difference to LocationContext is the reduced amount of cities that are generated
        Note: Not running in CI since it generates a lot of pages and uses functionalities which are test in the other tests
        """
        self.eventLocationContext.generateORLocationPages(self.eventCorpus.eventList,"/tmp/wikirender",True, 10)
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