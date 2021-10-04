from geograpy.locator import LocationContext, Locator
from ormigrate.issue220_location import LocationFixer
from ormigrate.toolbox import Profiler
from tests.pagefixtoolbox import PageFixerToolbox, PageFixerTest
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.toolbox import HelperFunctions as hf

class TestLocationFixer(PageFixerTest):
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

    @staticmethod
    def setUpLocationDb():
        '''Ensure the georapyDB is present'''
        if hf.inPublicCI():
            Locator.resetInstance()
            locator = Locator.getInstance()
            locator.downloadDB()
    
    def setUp(self):
        self.setUpLocationDb()
        PageFixerTest.setUp(self)
        self.pageFixerClass=LocationFixer
        self.testAll=False
        self.CITY=LocationFixer.CITY
        self.REGION=LocationFixer.REGION
        self.COUNTRY=LocationFixer.COUNTRY

    def testFixEventRecordExample(self):
        '''
        test fixing a single event record
        '''
        return
        # ToDo: Major cities of Bavaria currently not in geograpy3
        event={
            "pageTitle":"Test 2020",
            self.COUNTRY:"Germany",
            self.REGION:"Bavaria",   #ToDo: Change to Region once template argument is changed
            self.CITY: "Munich"
        }
        exp_event={
            "pageTitle":"Test 2020",
            self.COUNTRY:"DE",
            self.REGION:"DE/BY",   #ToDo: Change to Region once template argument is changed
            self.CITY: "DE/BY/Munich"
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertEqual(exp_event,res)
        self.assertTrue('complete' in errors and len(errors) == 1)
        self.assertEqual(exp_event.get(self.COUNTRY), event[self.COUNTRY])
        self.assertEqual(exp_event.get(self.REGION), event[self.REGION])
        self.assertEqual(exp_event.get(self.CITY), event[self.CITY])


    def test_fixEventRecord_invalid_country(self):
        """
        It is expected that the fixer can detect and correct a invalid country if city and region are correct and
        recognized.
        """
        profile = Profiler("Testing the correction invalid countries", self.profile)
        event={
            "pageTitle":"Test 2020",
            self.COUNTRY:"USA",
            self.REGION:"British Columbia",   #ToDo: Change to Region once template argument is changed
            self.CITY: "Vancouver"
        }
        exp_event={
            "pageTitle":"Test 2020",
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
            "pageTitle": "Test 2020",
            self.COUNTRY: "USA",
            self.CITY: "Los Angeles"
        }
        exp_event = {
            "pageTitle": "Test 2020",
            self.COUNTRY: "US",
            self.REGION: "US/CA",  # ToDo: Change to Region once template argument is changed
            self.CITY: "US/CA/Los Angeles"
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertDictEqual(exp_event, res)
        self.assertDictEqual({}, errors)
        profile.time()

    def test_fixEventRecord_missing_city(self):
        """
        It is expected that country and region entries are fixed and city entry stays missing
        """
        event = {
            "pageTitle": "Test 2020",
            self.COUNTRY: "Germany",
            self.REGION: "Bavaria"   # ToDo: Change to Region once template argument is changed
        }
        exp_event = {
            "pageTitle": "Test 2020",
            self.COUNTRY: "DE",
            self.REGION: "DE/BY",  # ToDo: Change to Region once template argument is changed
        }
        res, errors = self.fixer.fixEventRecord(event)
        self.assertDictEqual(exp_event, res)
        self.assertTrue("city_unknown" in errors)

    def test_fixEventRecord_invalid_city(self):
        """
        It is expected that country and region entries are fixed and city entry stays missing
        """
        event = {
            "pageTitle": "Test 2020",
            self.COUNTRY: "Germany",
            self.REGION: "Bavaria",   # ToDo: Change to Region once template argument is changed
            self.CITY: "EventLocation"
        }
        exp_event = {
            "pageTitle": "Test 2020",
            self.COUNTRY: "DE",
            self.REGION: "DE/BY",  # ToDo: Change to Region once template argument is changed
            self.CITY: "EventLocation"
        }
        res, errors = self.fixer.fixEventRecord(event)
        print(errors)
        self.assertDictEqual(exp_event, res)
        self.assertTrue("city_unknown" in errors)

    def test_get_page_title(self):
        '''tests the generation of the wiki page titles for location entities'''
        profile = Profiler("Testing generation of location page titles", self.profile)
        locationContext=LocationContext.fromCache()
        cities=locationContext.cityManager.getLocationsByWikidataId("Q65")
        la=cities[0]
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
        pageTitleLists=self.getPageTitleLists("ICKE 2022","AAC 2019","ETC 2021","CSCW 2021","ACNS 2016")
        for pageTitleList in pageTitleLists:
            counters=self.getRatingCounters(pageTitleList)
            painCounter=counters["pain"]
            if pageTitleList is None:
                self.assertTrue(painCounter[self.pageFixerClass.__name__][5]>1000)
            else:
                self.assertEqual(3,painCounter[self.pageFixerClass.__name__][5])

    def testRate(self):
        '''
        tests the rating of location values of eventRecords
        '''
        event_region_missing={
            "pageTitle":"Test",
            self.COUNTRY:"Germany",
            self.CITY:"Aachen"
        }
        entityRating_region_missing = PageFixerToolbox.getEntityRatingForRecord(event_region_missing)
        self.fixer.rate(entityRating_region_missing)
        self.assertEqual(entityRating_region_missing.pain, 5)

        event_invalid_city = {
            "pageTitle": "Test",
            self.COUNTRY: "Germany",
            self.CITY: "123456"
        }
        entityRating_invalid_city= PageFixerToolbox.getEntityRatingForRecord(event_invalid_city)
        self.fixer.rate(entityRating_invalid_city)
        self.assertEqual(entityRating_invalid_city.pain, 6)

        event_missing_locations = {"pageTitle":"Test"}
        entityRating_missing_locations  = PageFixerToolbox.getEntityRatingForRecord(event_missing_locations)
        self.fixer.rate(entityRating_missing_locations)
        self.assertEqual(entityRating_missing_locations.pain, 7)

        event_or_loc_labels= {"pageTitle": "Test",
                                   self.COUNTRY: "GR",
                                   self.REGION:"GR/I",
                                   self.CITY: "GR/I/Athens"
                                   }
        entityRating_or_loc_labels = PageFixerToolbox.getEntityRatingForRecord(event_or_loc_labels)
        self.fixer.rate(entityRating_or_loc_labels)
        self.assertEqual(entityRating_or_loc_labels.pain, 1)

    def testFix(self):
        eventRecord = {
            "pageTitle": "Test 2020",
            self.COUNTRY: "Germany",
            self.CITY: "Bavaria"
        }
        entityRating=PageFixerToolbox.getEntityRatingForRecord(eventRecord)
        self.fixer.fix(entityRating)
        print(entityRating.getRecord())

    def testCaching(self):
        '''Test caching of location information'''
        eventRecords = self.fixer.orDataSource.eventManager.getLoD()
        expectedLookups=2500
        if hf.inPublicCI() or not self.debug:
            eventRecords=eventRecords[:20]
            expectedLookups=10
        self.fixer.cacheLocations(eventRecords)
        self.assertTrue(len(self.fixer.locationTextLookup)>=expectedLookups)


    def testKnownLookupIssues(self):
        '''test ranking issues of found locations'''
        #return
        #ToDo: Improve ranking of geograpy
        # greenville in North Carolina is first answer even though the correct choice is on place three
        locations={
            "Q574192":["Greenville", "South Carolina", "USA"]
        }
        for wikidataId, locationParts in locations.items():
            foundLocation=self.fixer.getMatchingLocation(*locationParts)
            print(foundLocation)
            self.assertEqual(wikidataId, foundLocation.wikidataid)
