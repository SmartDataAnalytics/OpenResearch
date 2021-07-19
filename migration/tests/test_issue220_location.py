from unittest import TestCase
from geograpy.locator import LocationContext
from openresearch.event import Event
from ormigrate.issue220_location import LocationFixer
from ormigrate.toolbox import Profiler
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
        fixer=pageFixerManager.pageFixers["LocationFixer"]
        return fixer
    
    def setUp(self):
        self.debug=False
        self.testAll=True
        self.CITY=LocationFixer.CITY
        self.REGION=LocationFixer.REGION
        self.COUNTRY=LocationFixer.COUNTRY

    def testFixEventRecordExample(self):
        '''
        test fixing a single event record
        '''
        event={
            "Acronym":"Test 2020",
            self.COUNTRY:"Germany",
            self.REGION:"Bavaria",   #ToDo: Change to Region once template argument is changed
            self.CITY: "Munich"
        }
        exp_event={
            "Acronym":"Test 2020",
            self.COUNTRY:"DE",
            self.REGION:"DE/BY",   #ToDo: Change to Region once template argument is changed
            self.CITY: "DE/BY/Munich"
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertEqual(exp_event,res)
        self.assertTrue('complete' in errors and len(errors) == 1)

    def testFixEventRecordExamples(self):
        """
        tests location fixing on event object
        """
        eventRecord = {
            "Acronym": "Test 2020",
            self.COUNTRY: "Germany",
            self.REGION: "Bavaria",  # ToDo: Change to Region once template argument is changed
            self.CITY: "Munich"
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "DE",
            self.REGION: "DE/BY",  # ToDo: Change to Region once template argument is changed
            self.CITY: "DE/BY/Munich"
        }
        event=Event()
        event.fromDict(eventRecord)
        self.fixer.fixEvent(event)
        self.assertEqual(exp_event.get(self.COUNTRY), event.__dict__[self.COUNTRY])
        self.assertEqual(exp_event.get(self.REGION), event.__dict__[self.REGION])
        self.assertEqual(exp_event.get(self.CITY), event.__dict__[self.CITY])


    def test_fixEventRecord_invalid_country(self):
        """
        It is expected that the fixer can detect and correct a invalid country if city and region are correct and
        recognized.
        """
        profile = Profiler("Testing the correction invalid countries", self.profile)
        event={
            "Acronym":"Test 2020",
            self.COUNTRY:"USA",
            self.REGION:"British Columbia",   #ToDo: Change to Region once template argument is changed
            self.CITY: "Vancouver"
        }
        exp_event={
            "Acronym":"Test 2020",
            self.COUNTRY:"CA",
            self.REGION:"CA/BC",   #ToDo: Change to Region once template argument is changed
            self.CITY: "CA/BC/Vancouver"
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
            self.COUNTRY: "USA",
            self.CITY: "Los Angeles"
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "US",
            self.REGION: "US/CA",  # ToDo: Change to Region once template argument is changed
            self.CITY: "US/CA/Los Angeles"
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
            self.COUNTRY: "Germany",
            self.REGION: "Bavaria"   # ToDo: Change to Region once template argument is changed
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "DE",
            self.REGION: "DE/BY",  # ToDo: Change to Region once template argument is changed
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
            self.COUNTRY: "Germany",
            self.REGION: "Bavaria",   # ToDo: Change to Region once template argument is changed
            self.CITY: "invalid city name!!!"
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "DE",
            self.REGION: "DE/BY",  # ToDo: Change to Region once template argument is changed
            self.CITY: "invalid city name!!!"
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
            self.COUNTRY: "Germany",
            self.CITY: "Bavaria"
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "Germany",
            self.REGION: "Bavaria"
        }
        self.fixer.fixLocationType(event)
        self.assertEqual(exp_event, event)

        # Misplaced city
        event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "Germany",
            self.REGION: "Munich"
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "Germany",
            self.CITY: "Munich"
        }
        self.fixer.fixLocationType(event)
        self.assertEqual(exp_event, event)

        # Misplaced city, location, country
        event = {
            "Acronym": "Test 2020",
            self.REGION: "USA",
            self.CITY: "CA",
            self.COUNTRY: "Los Angeles"
        }
        exp_event = {
            "Acronym": "Test 2020",
            self.COUNTRY: "USA",
            self.REGION: "CA",
            self.CITY: "Los Angeles"
        }
        hasChangedPositions=self.fixer.fixLocationType(event)
        self.assertTrue(hasChangedPositions)
        self.assertEqual(exp_event[self.CITY], event[self.CITY])
        self.assertEqual(exp_event[self.REGION], event[self.REGION])
        self.assertEqual(exp_event[self.COUNTRY], event[self.COUNTRY])
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
        
    def testRating(self):
        '''
        test the rating
        '''
        pageTitleLists=PageFixerToolbox.getPageTitleLists("ICKE 2022","AAC 2019","ETC 2021","CSCW 2021","ACNS 2016",testAll=self.testAll)
        for pageTitleList in pageTitleLists:
            counters=PageFixerToolbox.getRatingCounters(self, pageTitleList, LocationFixer,debug=self.debug)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[5]>1000)
            else:
                self.assertEqual(3,painCounter[5])

    def testGetRating(self):
        '''
        tests the rating of location values of eventRecords
        '''
        event_region_missing={
            self.COUNTRY:"Germany",
            self.CITY:"Aachen"
        }
        rating_region_missing=self.fixer.getRating(event_region_missing)
        self.assertEqual(rating_region_missing.pain, 5)

        event_invalid_city = {
            self.COUNTRY: "Germany",
            self.CITY: "123456"
        }
        rating_region_missing = self.fixer.getRating(event_invalid_city)
        self.assertEqual(rating_region_missing.pain, 6)

        event_missing_locations = {}
        rating_missing_locations= self.fixer.getRating(event_missing_locations)
        self.assertEqual(rating_missing_locations.pain, 7)
        