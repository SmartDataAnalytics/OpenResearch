from geograpy.locator import Location, City, Country, Region
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer, Entity
from ormigrate.smw.rating import Rating, RatingType, EntityRating
from openresearch.openresearch import OpenResearch

class LocationFixer(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="fixes Locations"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/220"

    worksOn=[Entity.EVENT]
    
    # value of type attribute of Locations to be fixed
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(LocationFixer, self).__init__(pageFixerManager)
        LocationFixer.locationContext=OpenResearch.getORLocationContext()
        self.locationTextLookup={}


    def cacheLocations(self, eventRecords:list):
        '''Caches the identified locations form the given events'''
        locationCombinations={}
        for eventRecord in eventRecords:
            eventCity = eventRecord.get(self.CITY)
            eventRegion = eventRecord.get(self.REGION)
            eventCountry = eventRecord.get(self.COUNTRY)
            locationCombination=f"{eventCountry},{eventRegion},{eventCity}"
            locationCombinations[locationCombination]={"countryName":eventCountry, "regionName":eventRegion, "cityName":eventCity}
        total=len(locationCombinations)
        count=0
        for locationCombination, eventPlaces in locationCombinations.items():
            count+=1
            if self.debug:
                print(f"{count}/{total} Looked up location information")
            foundLocations=self.lookupLocation(**eventPlaces)
            if foundLocations:
                self.locationTextLookup[locationCombination]=foundLocations

    def lookupLocation(self, countryName:str=None, regionName:str=None, cityName:str=None):
        '''
        Uses geograpy3 to find locations matching the given information
        Args:
            countryName: name of the country
            regionName: name of the region
            cityName: name of the city

        Returns:
            List of locations that match the given location information
        '''
        eventPlaces = []
        for eventLocation in countryName, regionName, cityName:
            # filter out known invalid and None values
            if eventLocation in ["Online", "None", "N/A"]:
                eventLocation = None
            # Add eventLocations to event Places
            if eventLocation:
                if eventLocation.startswith("Category:"):
                    eventLocation = eventLocation.replace("Category:", "")
                if '/' in eventLocation:
                    eventPlaces.extend(eventLocation.split('/'))
                else:
                    eventPlaces.append(eventLocation)
        foundLocations = self.locationContext.locateLocation(*eventPlaces)
        return foundLocations

    def fix(self,rating:EntityRating):
        '''
        tries fixing the location entries of the  given entity
        '''
        eventRecord = rating.getRecord()
        self.fixEventRecord(eventRecord)

    def fixEventRecord(self, event:dict, errors:dict=None):
        '''
        Args:
            event(dict): event records containing the location values that should be fixed
            errors(dict): dictonary containing the errors of the given event record → new errors are added to the dict
        '''
        if errors is None:
            errors = {}
        eventCity = event.get(self.CITY)
        eventRegion = event.get(self.REGION)
        eventCountry = event.get(self.COUNTRY)
        # event Places could be extended with the event title
        locationCombination=f"{eventCountry},{eventRegion},{eventCity}"
        if locationCombination in self.locationTextLookup:
            foundLocations=self.locationTextLookup.get(locationCombination)
        else:
            foundLocations=self.lookupLocation(eventCountry, eventRegion, eventCity)
            self.locationTextLookup[locationCombination]=foundLocations
        # find best match
        foundCities = [l for l in foundLocations if isinstance(l, City) and getattr(l, 'pop') is not None]
        foundRegions = [l for l in foundLocations if isinstance(l, Region)]
        foundCountries = [l for l in foundLocations if isinstance(l, Country)]
        if foundCities:
            bestMatch=foundCities[0]
            event[self.CITY]=self.getPageTitle(bestMatch)
            event[self.REGION] = self.getPageTitle(bestMatch.region)
            event[self.COUNTRY] = self.getPageTitle(bestMatch.country)
        elif foundRegions:
            bestMatch = foundRegions[0]
            #event[self.CITY] = None
            event[self.REGION] = self.getPageTitle(bestMatch)
            event[self.COUNTRY] = self.getPageTitle(bestMatch.country)
            errors["city_unknown"] = f"Location information did not match any city"
        elif foundCountries:
            bestMatch = foundCountries[0]
            #event[self.CITY] = None
            #event[self.REGION] = None
            event[self.COUNTRY] = self.getPageTitle(bestMatch)
            errors["region_unknown"] = f"Location information did not match any region or city"
        else:
            errors["country_unknown"] = f"Location information did not match any location"
            #event[self.CITY] = None
            #event[self.REGION] = None
            #event[self.COUNTRY] = None
        return event, errors



    @staticmethod
    def getWikidataIds(locations: list):
        '''
        Returns a set of wikidataids of the given locations

        Args:
            locations(list): list of Locations

        Returns:
            List of wikidata ids from the locations of the given list
        '''
        res = {x.wikidataid for x in locations if 'wikidataid' in x.__dict__}
        return res

    @staticmethod
    def getPageTitle(location:Location):
        '''
        Returns the wiki page title for the given location
        The hierarchy of the location is hereby represented in the page title
        The page titles are constructed as follows:
            -Countries: country_isocode     e.g. US
            -Regions: country_isocode/region_isocode    e.g US/CA
            -Cities: country_isocode/region_isocode/city_name   e.g. US/CA/Los_Angeles

        Args:
            location(Location): location for which the corresponding wiki pageTitle should be returned

        Returns:
            wiki pageTitle of the given location as string
        '''
        pageTitle=None
        if isinstance(location, City):
            countryPart=getattr(location.country,'iso')
            regionPart=getattr(location.region,'iso').split('-')[1] if '-' in getattr(location.region,'iso') else getattr(location.region,'iso')
            pageTitle=f"{countryPart}/{regionPart}/{getattr(location, 'name')}"
        elif isinstance(location, Region):
            countryPart = getattr(location.country, 'iso')
            regionPart=getattr(location,'iso').split('-')[1] if '-' in getattr(location,'iso') else getattr(location, 'iso')
            pageTitle = f"{countryPart}/{regionPart}"
        elif isinstance(location, Country):
            pageTitle=getattr(location,'iso')
        else:
            pageTitle=location.name
        return pageTitle

    def rate(self, rating:EntityRating):
        '''
        get the pain Rating for the given eventRecord
        '''
        eventRecord=rating.getRecord()
        arating=self.getRating(eventRecord)
        rating.set(arating.pain, arating.reason, arating.hint)

    @classmethod
    def getRating(cls, eventRecord):
        painrating = None
        city = None
        region = None
        country = None

        if cls.CITY in eventRecord: city = eventRecord[cls.CITY]
        if cls.REGION in eventRecord: region = eventRecord[cls.REGION]
        if cls.COUNTRY in eventRecord: country = eventRecord[cls.COUNTRY]
        for location in [city,region,country]:
            if isinstance(location, str):
                location.replace("/",",")   # Adjust new or naming scheme to geograpy
        if not city and not region and not country:
            # location is not defined
            painrating=Rating(7, RatingType.missing,f'Locations are not defined')
        else:
            if hasattr(cls,'locationContext'):
                locationContext=getattr(cls,'locationContext')
                cities=[l for l in locationContext.locateLocation(city) if isinstance(l, City)]
                regions=[l for l in locationContext.locateLocation(region) if isinstance(l, Region)]
                countries=[l for l in   locationContext.locateLocation(country) if isinstance(l, Country)]
            if cities and regions and countries:
                # all locations are recognized
                painrating=Rating(1,RatingType.ok,f'Locations are valid. (Country: {country}, Region: {region}, City:{city})')
            elif not cities:
                # City is not valid
                painrating=Rating(6, RatingType.invalid,f'City is not recognized. (City:{city})')
            elif not regions:
                # City is valid but region is not
                painrating=Rating(5, RatingType.invalid,f'Region is not recognized. (Country: {country}, Region: {region}, City:{city})')
            else:
                # City and region are valid but country is not
                painrating=Rating(3, RatingType.invalid,f'Country is not recognized. (Country: {country}, Region: {region}, City:{city})')
        return painrating
    
if __name__ == '__main__':
    PageFixerManager.runCmdLine([LocationFixer])