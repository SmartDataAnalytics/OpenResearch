'''
Created on 2021-08-21

@author: wf
'''
import logging
import os
import unittest
from collections import Counter

from corpus.lookup import CorpusLookup
from lodstorage.query import Query, QueryManager
from lodstorage.tabulateCounter import TabulateCounter

from tests.corpusfortesting import CorpusForTesting
from tests.pagefixtoolbox import PageFixerTest
from openresearch.openresearch import OpenResearch
from OSMPythonTools.nominatim import Nominatim

class TestIssue228(PageFixerTest):
    '''
    Invalid entries for country
    '''
    
    def setUp(self):
        '''
        setuUp 
        '''
        super().setUp(debug=False)
        self.orDataSource=CorpusForTesting.getEventDataSourceFromWikiText()
        self.locationContext=OpenResearch.getORLocationContext()
        cacheRootDir = self.locationContext.getDefaultConfig().cacheRootDir
        cacheDir = f"{cacheRootDir}/.nominatim"
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
        self.nominatim = Nominatim(cacheDir=cacheDir)
        logging.getLogger('OSMPythonTools').setLevel(logging.ERROR)

        self.getCountries()
        
    def getCountries(self):
        '''
        load countries
        '''
        countryManager=self.locationContext.countryManager
        countryManager.fromCache()
        self.countriesByIso,_dup=countryManager.getLookup("iso")
        self.assertTrue(len(_dup)<=1)

    def lookupNominatim(self, locationText: str):
        '''
        Uses nominatim to resolve the given location text into a wikidataid.
        This wikidataid is then used to get the corresponding location object from georapy
        Args:
            locationText:

        Returns:
            Location object corresponding to the given locationText
        '''
        location = None
        nresult = self.nominatim.query(locationText, params={"extratags": "1"})
        nlod = nresult._json
        if len(nlod) > 0:
            nrecord = nlod[0]
            if "extratags" in nrecord:
                extratags = nrecord["extratags"]
                if "wikidata" in extratags:
                    wikidataID = extratags["wikidata"]
                    location = self.getCountryByWikiDataId(wikidataID)
        return location

    def getCountryByWikiDataId(self, wikidataID: str):
        '''
        get the country for the given wikidataID
        '''
        countryById=self.locationContext.countryManager.locationByWikidataID
        country=countryById.get(wikidataID)
        return country

    def getCounter(self, events: list, propertyName: str):
        '''
        get a counter for the given propertyName
        '''
        counter = Counter()
        for event in events:
            if hasattr(event, propertyName):
                value = getattr(event, propertyName)
                if value is not None:
                    counter[value] += 1
        tabCounter = TabulateCounter(counter)
        return counter, tabCounter

    def cacheNominatimCountries(self,limit:int=None,show:bool=True):
        '''
        Cache Nominatim results for the countries used in openresearch
        '''
        events=self.orDataSource.eventManager.getList()
        pCount, _pCountTab=self.getCounter(events, 'country')
        count=len(pCount.items())
        total=sum(pCount.values())
        rsum=0
        problems=[]
        invalidCountries=[]
        for i, locationTuple in enumerate(pCount.most_common(limit)):
            locationText, locationCount=locationTuple
            rsum+=locationCount
            percent=rsum / total * 100
            country=None
            try:
                country = self.lookupNominatim(locationText)
            except Exception as ex:
                print(str(ex))
                country=None
            if show:
                if country:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)✅:{locationText}({locationCount})→{country}")
                else:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)❌:{locationText if locationText else '<None>'}({locationCount})")
                    invalidCountries.append(locationText)
        if show:
            self.printInvalidCountries(invalidCountries)

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
        if self.debug:
            show=True
        else:
            show=False
        limit=10
        self.cacheNominatimCountries(limit, show=show)
        pass


if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()