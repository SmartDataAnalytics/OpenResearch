'''
Created on 2021-04-13

@author: wf
'''
import unittest
from migration.openresearch.event import CountryList

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


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()