from unittest import TestCase
from geograpy.locator import LocationContext
from openresearch.event import Event
from ormigrate.issue220_location import LocationFixer
from ormigrate.toolbox import Profiler
from tests.corpusfortesting import CorpusForTesting
from tests.pagefixtoolbox import PageFixerToolbox
from ormigrate.fixer import PageFixerManager

class TestLocationFixer(TestCase):
    '''
    test location fixer
    '''

    @classmethod
    def setUpClass(cls):
        cls.profile=True
        cls.fixer=cls.getFixer()
    
    @classmethod
    def getFixer(self):
        argv=PageFixerToolbox.getArgs(None,["--stats"],debug=self.debug)
        pageFixerManager=PageFixerManager.fromCommandLine([LocationFixer], argv)
        wikiFileManager = CorpusForTesting.getWikiFileManager()
        fixer=LocationFixer(wikiFileManager=wikiFileManager)
        return fixer

    def test_fixEventRecord(self):
        '''
        test fixing a single event record
        '''
        event={
            "Acronym":"Test 2020",
            "Country":"Germany",
            "State":"Bavaria",   #ToDo: Change to Region once template argument is changed
            "City": "Munich"
        }
        exp_event={
            "Acronym":"Test 2020",
            "Country":"DE",
            "State":"DE/BY",   #ToDo: Change to Region once template argument is changed
            "City": "DE/BY/Munich"
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertEqual(exp_event,res)
        self.assertTrue('complete' in errors and len(errors) == 1)

    def test_fixEvent(self):
        """
        tests location fixing on event object
        """
        eventRecord = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "State": "Bavaria",  # ToDo: Change to Region once template argument is changed
            "City": "Munich"
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "DE",
            "State": "DE/BY",  # ToDo: Change to Region once template argument is changed
            "City": "DE/BY/Munich"
        }
        event=Event()
        event.fromDict(eventRecord)
        self.fixer.fixEvent(event)
        self.assertEqual(exp_event.get("Country"), event.Country)
        self.assertEqual(exp_event.get("State"), event.State)
        self.assertEqual(exp_event.get("City"), event.City)


    def test_fixEventRecord_invalid_country(self):
        """
        It is expected that the fixer can detect and correct a invalid country if city and region are correct and
        recognized.
        """
        profile = Profiler("Testing the correction invalid countries", self.profile)
        event={
            "Acronym":"Test 2020",
            "Country":"USA",
            "State":"British Columbia",   #ToDo: Change to Region once template argument is changed
            "City": "Vancouver"
        }
        exp_event={
            "Acronym":"Test 2020",
            "Country":"CA",
            "State":"CA/BC",   #ToDo: Change to Region once template argument is changed
            "City": "CA/BC/Vancouver"
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertEqual(exp_event,res)
        profile.time()

    def test_fixEventRecord_missing_entries(self):
        """
        It is expected that missing entries are detected and fixed
        """
        profile = Profiler("Testing detecting and fixing of missing location entries in event records", self.profile)
        event = {
            "Acronym": "Test 2020",
            "Country": "USA",
            "City": "Los Angeles"
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "US",
            "State": "US/CA",  # ToDo: Change to Region once template argument is changed
            "City": "US/CA/Los Angeles"
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertEqual(exp_event, res)
        self.assertTrue("region_missing" in errors)
        profile.time()

    def test_fixEventRecord_missing_city(self):
        """
        It is expected that country and region entries are fixed and city entry stays missing
        """
        event = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "State": "Bavaria"   # ToDo: Change to Region once template argument is changed
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "DE",
            "State": "DE/BY",  # ToDo: Change to Region once template argument is changed
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertEqual(exp_event, res)
        self.assertTrue("city_missing" in errors)

    def test_fixEventRecord_invalid_city(self):
        """
        It is expected that country and region entries are fixed and city entry stays missing
        """
        event = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "State": "Bavaria",   # ToDo: Change to Region once template argument is changed
            "City": "invalid city name!!!"
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "DE",
            "State": "DE/BY",  # ToDo: Change to Region once template argument is changed
            "City": "invalid city name!!!"
        }
        res, errors = self.fixer.fixEventRecord(event)
        print(errors)
        self.assertEqual(exp_event, res)
        self.assertTrue("city_unrecognized" in errors)


    def testFixLocationType(self):
        '''
        tests the correction of misplaced locations
        '''
        profile = Profiler("Testing the correction of misplaced locations", self.profile)
        # Misplaced region
        event = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "City": "Bavaria"
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "State": "Bavaria"
        }
        self.fixer.fixLocationType(event)
        self.assertEqual(exp_event, event)

        # Misplaced city
        event = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "State": "Munich"
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "Germany",
            "City": "Munich"
        }
        self.fixer.fixLocationType(event)
        self.assertEqual(exp_event, event)

        # Misplaced city, location, country
        event = {
            "Acronym": "Test 2020",
            "State": "USA",
            "City": "CA",
            "Country": "Los Angeles"
        }
        exp_event = {
            "Acronym": "Test 2020",
            "Country": "USA",
            "State": "CA",
            "City": "Los Angeles"
        }
        hasChangedPositions=self.fixer.fixLocationType(event)
        self.assertTrue(hasChangedPositions)
        self.assertEqual(exp_event["City"], event["City"])
        self.assertEqual(exp_event["State"], event["State"])
        self.assertEqual(exp_event["Country"], event["Country"])
        profile.time()

    def test_get_page_title(self):
        '''tests the generation of the wiki page titles for location entities'''
        profile = Profiler("Testing generation of location page titles", self.profile)
        locationContext=LocationContext.fromJSONBackup()
        la=None
        for city in locationContext.cities:
            if 'wikidataid' in city.__dict__ and city.wikidataid=="Q65":
                la=city
                break
        if la is not None:
            ca=la.region
            us=la.country
            self.assertEqual("US", LocationFixer.getPageTitle(us))
            self.assertEqual("US/CA", LocationFixer.getPageTitle(ca))
            self.assertEqual("US/CA/Los Angeles", LocationFixer.getPageTitle(la))
        else:
            self.fail("City Q65 (Los Angeles) is missing in the locationContext")
        profile.time()