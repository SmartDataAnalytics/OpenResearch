'''
Created on 22.08.2021

@author: wf
'''
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
        
    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super().__init__(pageFixerManager)
        self.locationContext=OpenResearch.getORLocationContext()
        self.getCountries()
        
    def getCountries(self):
        '''
        load countries
        '''
        countryManager=self.locationContext.countryManager
        countryManager.fromCache()
        self.countriesByIso,_dup=countryManager.getLookup("iso")
        self.duplicateCountryCount=len(_dup)
        
    def cacheNominatim(self):
        '''
        loop over most common locations by using country, region and city as loctionText
        and ask Noninatim for the correspoding wikidataID which should mostly be a city
        but could also be a region or country
        '''
        
        
if __name__ == '__main__':
    PageFixerManager.runCmdLine([CountryFixer])