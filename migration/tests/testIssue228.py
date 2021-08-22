'''
Created on 2021-08-21

@author: wf
'''
import logging
import os
import unittest
from ormigrate.issue228_country import CountryFixer
from lodstorage.query import Query, QueryManager
from tests.pagefixtoolbox import PageFixerTest
from openresearch.openresearch import OpenResearch

class TestIssue228(PageFixerTest):
    '''
    Invalid entries for country
    '''
    
    def setUp(self):
        '''
        setuUp 
        '''
        super().setUp(debug=False)
        self.pageFixerClass=CountryFixer

    def printInvalidCountries(self, invalidCountries:list=None):
        '''

        Args:
            invalidCountries: names of countries that could not be directly identified as countries

        Returns:
            prints table of invalid country names and the a link to the corresponding wiki
        '''
        eventsByLocation = self.orDataSource.eventManager.getLookup('country', withDuplicates=True)
        queryManager=self.getQueryManager()
        query=queryManager.queriesByName['Issue 228 countries occurring once']
        sqlDb=self.orDataSource.eventManager.getSQLDB(self.orDataSource.eventManager.cacheFile)
        qRes=sqlDb.query(query.query)
        lod=[]
        for record in qRes:
            record['url']=record['url'].replace("//orindex", "/or/index").replace(" ","_")   #ToDo: Fix generation of the url in ConferenceCorpus
            if record['country'] in invalidCountries:
                lod.append(record)
        print(query.documentQueryResult(lod=lod, tablefmt="github"))

    def getQueryManager(self):
        '''
        get the query manager
        '''
        path = OpenResearch.getResourcePath()
        qYamlPath = f"{path}/queries.yaml"
        if os.path.isfile(qYamlPath):
            qm = QueryManager(lang='sql', debug=self.debug, path=path)
            return qm
        return None

    def testIssue228(self):
        '''
        check for Invalid countries
        '''
        fixer = self.getPageFixer()
        self.assertTrue(len(fixer.countriesByIso)>200)
        if self.debug:
            self.printInvalidCountries(fixer.invalidCountryNames)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()