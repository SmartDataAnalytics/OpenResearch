from unittest import TestCase

from ormigrate.issue220_location import LocationFixer
from ormigrate.toolbox import HelperFunctions as hf

class TestLocationFixer(TestCase):
    
    def getFixer(self):
        fixer=LocationFixer(wikiClient=hf.getWikiClient(save=hf.inPublicCI()))
        return fixer

    def test_fixEventRecord(self):
        fixer=self.getFixer()
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
        res, errors = fixer.fixEventRecord(event)
        self.assertEqual(exp_event,res)
        self.assertTrue('complete' in errors and len(errors) == 1)


    def test_fixEventRecord_invalid_country(self):
        """
        It is expected that the fixer can detect and correct a invalid country if city and region are correct and
        recognized.
        """
        fixer=self.getFixer()
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
        res, errors = fixer.fixEventRecord(event)
        self.assertEqual(exp_event,res)

    def test_fixEventRecord_missing_entries(self):
        """
        It is expected that missing entries are detected and fixed
        """
        fixer = self.getFixer()
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
        res, errors = fixer.fixEventRecord(event)
        self.assertEqual(exp_event, res)
        self.assertTrue("region_missing" in errors)

    def test_fixEventRecord_missing_city(self):
        """
        It is expected that country and region entries are fixed and city entry stays missing
        """
        fixer = self.getFixer()
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
        res, errors = fixer.fixEventRecord(event)
        self.assertEqual(exp_event, res)
        self.assertTrue("city_missing" in errors)

    def test_fixEventRecord_invalid_city(self):
        """
        It is expected that country and region entries are fixed and city entry stays missing
        """
        fixer = self.getFixer()
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
        res, errors = fixer.fixEventRecord(event)
        print(errors)
        self.assertEqual(exp_event, res)
        self.assertTrue("city_unrecognized" in errors)


    def testFixLocationType(self):
        # Misplaced region
        fixer = self.getFixer()
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
        fixer.fixLocationType(event)
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
        fixer.fixLocationType(event)
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
        hasChangedPositions=fixer.fixLocationType(event)
        self.assertTrue(hasChangedPositions)
        self.assertEqual(exp_event["City"], event["City"])
        self.assertEqual(exp_event["State"], event["State"])
        self.assertEqual(exp_event["Country"], event["Country"])