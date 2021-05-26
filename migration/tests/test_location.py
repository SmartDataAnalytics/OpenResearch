from unittest import TestCase
from openresearch.location import *


class TestLocation(TestCase):
    location_sample = {
        "name": "Los Angeles",
        "wikidataid": "Q65",
        "coordinates": "34.05223,-118.24368",
        "partOf": "US/CA",
        "level": 5,
        "locationKind": "City",
        "comment": None,
        "population": 3976322
    }

    def test_add_label(self):
        location = Location(**self.location_sample)
        location.addLabel("LA")
        self.assertTrue(len(location.labels) == 1)
        self.assertTrue("LA" in location.labels)

    def test_is_known_as(self):
        location = Location(**self.location_sample)
        location.addLabel("LA")
        self.assertTrue(location.isKnownAs("LA"))
        self.assertTrue(location.isKnownAs("Los Angeles"))
        self.assertFalse(location.isKnownAs("Berlin"))


class TestCountry(TestCase):

    def test_parameter_assignment(self):
        country_sample = Region.getSamples()[0]
        country = Country(**country_sample)
        for (key, value) in country_sample.items():
            self.assertEqual(value, country.__dict__[key])

    def test_get_page_title(self):
        country_sample = {
            "name": "United States of America",
            "wikidataid": "Q30",
            "coordinates": "39.82818, -98.5795",
            "partOf": "North America",
            "level": 3,
            "locationKind": "Country",
            "comment": None,
            "labels": ["USA", "US", "United States of America"],
            "isocode": "US"
        }
        country = Country(**country_sample)
        self.assertEqual("US", country.getPageTitle())


class TestRegion(TestCase):

    def test_parameter_assignment(self):
        region_sample = Region.getSamples()[0]
        region = Region(**region_sample)
        for (key, value) in region_sample.items():
            self.assertEqual(value, region.__dict__[key])

    def test_get_page_title(self):
        region_sample = {
            "name": "California",
            "wikidataid": "Q99",
            "coordinates": "37.0,-120.0",
            "partOf": "US",
            "level": 4,
            "locationKind": "Region",
            "comment": None,
            "labels": ["CA", "California"],
            "isocode": "US-CA"
        }
        region = Region(**region_sample)
        self.assertEqual("US/CA", region.getPageTitle())


class TestCity(TestCase):

    def test_parameter_assignment(self):
        city_sample = City.getSamples()[0]
        city = City(**city_sample)
        for (key, value) in city_sample.items():
            self.assertEqual(value, city.__dict__[key])

    def test_get_page_title(self):
        city_sample = {
            "name": "Los Angeles",
            "wikidataid": "Q65",
            "coordinates": "34.05223,-118.24368",
            "partOf": "US/CA",
            "level": 5,
            "locationKind": "City",
            "comment": None,
            "population": "3976322"
        }
        city = City(**city_sample)
        self.assertEqual("US/CA/Los Angeles", city.getPageTitle())


class TestCountryList(TestCase):

    def testCountryListLoading(self):
        countries = CountryList().restoreFromJsonFile('../ormigrate/resources/countries')
        # USA is a country that should always be in the list test if present
        us_present = False
        for country in countries:
            if 'wikidataid' in country.__dict__:
                if country.wikidataid == "Q30":
                    us_present = True
                    break
        self.assertTrue(us_present)


class TestRegionList(TestCase):

    def testRegionListLoading(self):
        regions = RegionList().restoreFromJsonFile('../ormigrate/resources/regions')
        # California is a region that should always be in the list test if present
        ca_present = False
        for region in regions:
            if 'wikidataid' in region.__dict__:
                if region.wikidataid == "Q99":
                    ca_present = True
                    break
        self.assertTrue(ca_present)


class TestCityList(TestCase):

    def testCityListLoading(self):
        cities = CityList().restoreFromJsonFile('../ormigrate/resources/cities')
        # Los Angeles is a city that should always be in the list test if present
        la_present = False
        for city in cities:
            if 'wikidataid' in city.__dict__:
                if city.wikidataid == "Q65":
                    la_present = True
                    break
        self.assertTrue(la_present)


class TestLocationCorpus(TestCase):

    def test_LocationCorpus(self):
        locationCorpus = LocationCorpus()
        city_LA = [city for city in locationCorpus.cities if city.wikidataid == "Q65"][0]
        self.assertEqual("Q65", city_LA.wikidataid)
        self.assertEqual("Q99", city_LA.getRegion().wikidataid)
        self.assertEqual("Q30", city_LA.getCountry().wikidataid)

    def test_getCountry(self):
        locationCorpus = LocationCorpus()
        countries=locationCorpus.getCountry("USA")
        self.assertTrue(len(countries)>=1)
        US_present = False
        for country in countries:
            if 'wikidataid' in country.__dict__:
                if country.wikidataid == "Q30":
                    US_present = True
                    break
        self.assertTrue(US_present)

    def test_getRegion(self):
        locationCorpus = LocationCorpus()
        regions=locationCorpus.getRegion("CA")
        self.assertTrue(len(regions)>=1)
        CA_present = False
        for region in regions:
            if 'wikidataid' in region.__dict__:
                if region.wikidataid == "Q99":
                    CA_present = True
                    break
        self.assertTrue(CA_present)

    def test_getCity(self):
        locationCorpus = LocationCorpus()
        cities=locationCorpus.getCity("LA")
        self.assertTrue(len(cities)>=1)
        LA_present = False
        for city in cities:
            if 'wikidataid' in city.__dict__:
                if city.wikidataid == "Q65":
                    LA_present = True
                    break
        self.assertTrue(LA_present)
