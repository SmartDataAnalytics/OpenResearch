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
        self.locationRatingLookup={}


    def cacheLocations(self, eventRecords:list):
        '''Caches the identified locations form the given events'''
        locationCombinations={}
        for eventRecord in eventRecords:
            eventCity = eventRecord.get(self.CITY)
            eventRegion = eventRecord.get(self.REGION)
            eventCountry = eventRecord.get(self.COUNTRY)
            locationCombination=f"{eventCountry},{eventRegion},{eventCity}"
            locationCombinations[locationCombination]={ "cityName":eventCity,"regionName":eventRegion, "countryName":eventCountry}
        total=len(locationCombinations)
        count=0
        for locationCombination, eventPlaces in locationCombinations.items():
            count+=1
            if self.debug:
                print(f"{count}/{total} Looked up location information")
            bestMatchingLoc=self.getMatchingLocation(*eventPlaces.values())
            if bestMatchingLoc:
                self.locationTextLookup[locationCombination]=bestMatchingLoc

    def getMatchingLocation(self, city:str=None, region:str=None, country:str=None):
        """
        Uses geograpy3 to retrieve the best match for the given location information by ranking the results of geograpy
        Args:
            city:
            region:
            country:

        Returns:
            Location
        """
        foundLocations = LocationFixer.locationContext.locateLocation(city, region, country)
        if foundLocations:
            #find best match
            rankedLocs=[]
            for loc in foundLocations:
                rank=0
                checkLocation=loc
                if isinstance(checkLocation, City):
                    if city in self.locationAlsoKnownAs(checkLocation):
                        rank+=3
                    checkLocation=checkLocation.region
                if isinstance(checkLocation, Region):
                    if region in self.locationAlsoKnownAs(checkLocation):
                        rank+=2
                    checkLocation=checkLocation.country
                if isinstance(checkLocation, Country):
                    if country in self.locationAlsoKnownAs(checkLocation):
                        rank+=1
                rankedLocs.append((loc,rank))
            # Postprocess ranking for known issues
            for i, t in enumerate(rankedLocs):
                loc, rank=t
                if "Brussels" in [city, region, country] and loc.wikidataid=='Q239': rank+=3
                rankedLocs[i]=(loc, rank)
            rankedLocs.sort(key=lambda x:x[1], reverse=True)
            maxRank=rankedLocs[0][1]
            bestMatches=[loc for loc, rank in rankedLocs if rank==maxRank]
            bestMatches.sort(key=lambda loc: float(loc.population) if hasattr(loc, "population") and getattr(loc, "population") else 0.0,reverse=True)
            return bestMatches[0]
        else:
            return None

    def locationAlsoKnownAs(self, location:Location) -> list:
        """
        Returns all labels of the given location
        """
        locationContext=LocationFixer.locationContext
        sqlDb = locationContext.cityManager.getSQLDB(locationContext.cityManager.getCacheFile())
        table = "CityLookup"
        if isinstance(location, Country): table="CountryLookup"
        elif isinstance(location, Region): table="RegionLookup"
        query = f"""
        SELECT label
        FROM { table }
        WHERE wikidataid == '{ location.wikidataid }'
        """
        queryRes = sqlDb.query(query)
        return [record.get('label') for record in queryRes]


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
        locationCombination = f"{countryName},{regionName},{cityName}"
        if locationCombination in self.locationTextLookup:
            bestMatch=self.locationTextLookup.get(locationCombination)
            return bestMatch
        else:
            eventPlaces = {
                'city':cityName,
                'region':regionName,
                'country':countryName
            }
            for prop, value in eventPlaces.items():
                # filter out known invalid and None values
                if value in ["Online", "None", "N/A"]:
                    value = None
                # Add eventLocations to event Places
                if value:
                    if value.startswith("Category:"):
                        value = value.replace("Category:", "")
                    if '/' in value:
                        value=value.split('/')[-1]
                eventPlaces[prop]=value
            bestMatch = self.getMatchingLocation(**eventPlaces)
            self.locationTextLookup[locationCombination] = bestMatch
            return bestMatch

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

        bestMatch=self.lookupLocation(eventCountry, eventRegion, eventCity)
        if isinstance(bestMatch, City):
            event[self.CITY]=self.getPageTitle(bestMatch)
            event[self.REGION] = self.getPageTitle(bestMatch.region)
            event[self.COUNTRY] = self.getPageTitle(bestMatch.country)
        elif isinstance(bestMatch, Region):
            #event[self.CITY] = None
            event[self.REGION] = self.getPageTitle(bestMatch)
            event[self.COUNTRY] = self.getPageTitle(bestMatch.country)
            errors["city_unknown"] = f"Location information did not match any city"
        elif isinstance(bestMatch, Country):
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

    def getRating(cls, eventRecord):
        painrating = None
        city = None
        region = None
        country = None

        if cls.CITY in eventRecord and eventRecord[cls.CITY] : city = eventRecord[cls.CITY]
        if cls.REGION in eventRecord and eventRecord[cls.REGION]: region = eventRecord[cls.REGION].replace("/",",")
        if cls.COUNTRY in eventRecord and eventRecord[cls.COUNTRY]: country = eventRecord[cls.COUNTRY].replace("/",",")

        if not city and not region and not country:
            # location is not defined
            painrating=Rating(7, RatingType.missing,f'Locations are not defined')
        else:
            if hasattr(LocationFixer,'locationContext'):
                cities=cls.getLocationsOfType(city, City)
                regions=cls.getLocationsOfType(region, Region)
                countries=cls.getLocationsOfType(country, Country)
            if (cities and regions and countries) or (city in [cls.getPageTitle(city) for city in cities]):
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

    def getLocationsOfType(self, locationName: str, type: Location):
        if locationName in self.locationRatingLookup:
            locs=self.locationRatingLookup[locationName]
        elif locationName is None:
            return []
        else:
            locs=LocationFixer.locationContext.locateLocation(locationName.replace("/",","))
            self.locationRatingLookup[locationName]=locs
        locsOfType = [l for l in locs if isinstance(l, type)]
        return locsOfType

    
if __name__ == '__main__':
    PageFixerManager.runCmdLine([LocationFixer])