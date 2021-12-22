'''
Created on 22.08.2021

@author: wf
'''
import logging
import os
from collections import Counter

from OSMPythonTools.cachingStrategy import CachingStrategy, JSON
from OSMPythonTools.nominatim import Nominatim
from corpus.lookup import CorpusLookup
from lodstorage.tabulateCounter import TabulateCounter

from ormigrate.fixer import ORFixer
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from openresearch.openresearch import OpenResearch

class CountryFixer(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="fixes Countries"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/228"
        
    def __init__(self,pageFixerManager:PageFixerManager):
        '''
        Constructor
        '''
        super().__init__(pageFixerManager)
        self.locationContext=OpenResearch.getORLocationContext()
        self.getCountries()
        self.locationContext = OpenResearch.getORLocationContext()
        cacheRootDir = self.locationContext.getDefaultConfig().cacheRootDir
        cacheDir = f"{cacheRootDir}/.nominatim"
        if not os.path.exists(cacheDir):
            os.makedirs(cacheDir)
        CachingStrategy.use(JSON, cacheDir=cacheDir)
        self.nominatim = Nominatim()
        logging.getLogger('OSMPythonTools').setLevel(logging.ERROR)
        self.invalidCountryNames = self.cacheNominatim(show=self.debug)
        
    def getCountries(self):
        '''
        load countries
        '''
        countryManager=self.locationContext.countryManager
        countryManager.fromCache()
        self.countriesByIso,_dup=countryManager.getLookup("iso")
        self.duplicateCountryCount=len(_dup)

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
        
    def cacheNominatim(self,show:bool=True):
        '''
        loop over most common locations by using country, region and city as loctionText
        and ask Noninatim for the correspoding wikidataID which should mostly be a city
        but could also be a region or country

        Args:
            show(bool): Show progress of the caching

        Return:
            List of names that could not be identified as countries
        '''
        events = self.orDataSource.eventManager.getList()
        pCount, _pCountTab = self.getCounter(events, 'country')
        count = len(pCount.items())
        total = sum(pCount.values())
        rsum = 0
        problems = []
        invalidCountries = []
        for i, locationTuple in enumerate(pCount.most_common()):
            locationText, locationCount = locationTuple
            rsum += locationCount
            percent = rsum / total * 100
            country = None
            try:
                country = self.lookupNominatim(locationText)
            except Exception as ex:
                print(str(ex))
                country = None
            if show:
                if country:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)✅:{locationText}({locationCount})→{country}")
                else:
                    print(f"{i:4d}/{count:4d}{rsum:6d}/{total:5d}({percent:4.1f}%)❌:{locationText if locationText else '<None>'}({locationCount})")
                    invalidCountries.append(locationText)
        return invalidCountries
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([CountryFixer])