'''
Created on 2021-04-13

@author: wf
'''
import unittest
from migration.openresearch.event import CountryList
from migration.migrate.toolbox import HelperFunctions as hf

class TestIssue146(unittest.TestCase):
    '''
    tests for https://github.com/SmartDataAnalytics/OpenResearch/issues/146
    Inconsistent location names
    '''

    def setUp(self):
        self.debug=False
        pass


    def tearDown(self):
        pass


    def testCountryList(self):
        '''
        test the countryList handling
        '''
        countryList=CountryList()
        countryList.getDefault()
        countries=countryList.countries
        self.assertIsNotNone(countries)
        if self.debug:
            for country in sorted(countries,key=lambda country: country.name):
                print(country)
        self.assertTrue(len(countries)>40)
        pass
    
    def testCountryFromWiki(self):
        '''
        test the countryList from Wiki handling
        '''
        wikiUser=hf.getSMW_WikiUser("cr", save=hf.inPublicCI())
        self.assertIsNotNone(wikiUser)
        countryList=CountryList()
        #countryList.debug=True
        countryList.fromWiki(wikiUser)
        countriesByName,duplicates=countryList.getLookup('name')
        self.assertEqual(0,len(duplicates))
        #print(countriesByName)
        self.assertTrue("New Zealand" in countriesByName)
       
    def testIssue167(self):
        '''
        https://github.com/SmartDataAnalytics/OpenResearch/issues/167
        
        add Lookup option for entityLists
        '''
        countryList=CountryList()
        countryList.getDefault()
        countries=countryList.countries
        #self.debug=True
        if self.debug:
            for country in sorted(countries,key=lambda country: country.wikidataId):
                print("%s: %s" % (country.wikidataId,country))
        countriesByWikiDataId,duplicates=countryList.getLookup('wikidataId')
        self.assertEqual(3,len(duplicates))
        self.assertTrue("Q16" in countriesByWikiDataId)
        


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()