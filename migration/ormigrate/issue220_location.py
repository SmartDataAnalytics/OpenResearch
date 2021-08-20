from geograpy.locator import LocationContext, Location, City, Country, Region
from ormigrate.smw.pagefixer import PageFixerManager
from ormigrate.fixer import ORFixer
from ormigrate.smw.rating import Rating, RatingType, EntityRating


class LocationFixer(ORFixer):
    '''
    see purpose and issue
    '''
    purpose="fixes Locations"
    issue="https://github.com/SmartDataAnalytics/OpenResearch/issues/220"
    
    # value of type attribute of Locations to be fixed
    COUNTRY = "country"
    REGION = "region"
    CITY = "city"

    def __init__(self,pageFixerManager):
        '''
        Constructor
        '''
        super(LocationFixer, self).__init__(pageFixerManager)
        LocationFixer.locationContext=self.getORLocationContext()

    def fix(self,rating:EntityRating):
        '''
        tries fixing the location entries of the  given entity
        '''
        eventRecord = rating.getRecord()
        self.fixEventRecord(eventRecord)

    def fixEventRecord(self, event:dict, errors:dict=None, bestFit=True):
        '''
        Args:
            event(dict): event records containing the location values that should be fixed
            errors(dict): dictonary containing the errors of the given event record → new errors are added to the dict
            bestFit(bool): If true the best/closed fit for a location is chosen (e.g. city with highest population). Otherwise a fix is only applied if the location can be identified with certainty.
        '''
        if errors is None:
            errors = {}
        eventCity = event.get(self.CITY)
        eventRegion = event.get(self.REGION)
        eventCountry = event.get(self.COUNTRY)
        eventPlaces=[]
        for eventLocation in eventCountry, eventRegion, eventCity:
            # filter out known invalid and None values
            if eventLocation in ["Online", "None", "N/A"]:
                eventLocation=None
            # Add eventLocations to event Places
            if eventLocation:
                if eventLocation.startswith("Category:"):
                    eventLocation=eventLocation.replace("Category:","")
                if '/' in eventLocation:
                    eventPlaces.extend(eventLocation.split('/'))
                else:
                    eventPlaces.append(eventLocation)
        # event Places could be extended with the event title
        foundLocations=self.locationContext.locateLocation(*eventPlaces)
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
            if 'name' in location.__dict__:
                nameCity=location.__dict__.get('name')
                isoParts=nameCity.split("-")
                isoRegion = LocationFixer.getPageTitle(location.region)
                if isoRegion is not None:
                    pageTitle=f"{isoRegion}/{nameCity}"
                else:
                    pageTitle=None
        elif isinstance(location, Region):
            if 'iso' in location.__dict__:
                isoRegion=location.__dict__.get('iso')
                isoParts=isoRegion.split("-")
                isoCountry = LocationFixer.getPageTitle(location.country)
                if len(isoParts) == 2:
                    # assumed iso format of regions US-CA
                    isoRegion=isoParts[1]
                    if isoCountry is None:
                        isoCountry=isoParts[0]
                    pageTitle=f"{isoCountry}/{isoRegion}"
                else:
                    pageTitle=None
        elif isinstance(location, Country):
            if 'iso' in location.__dict__:
                pageTitle=location.__dict__.get('iso')
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
        if not city and not region and not country:
            # location is not defined
            painrating=Rating(7, RatingType.missing,f'Locations are not defined')
        else:
            if 'locationContext' in cls.__dict__:
                cities=[l for l in getattr(cls,'locationContext').locateLocation(city) if isinstance(l, City)]
                regions=[l for l in getattr(cls,'locationContext').locateLocation(region) if isinstance(l, Region)]
                countries=[l for l in getattr(cls,'locationContext').locateLocation(country) if isinstance(l, Country)]
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

    @staticmethod
    def getORLocationContext():
        '''
        Returns a LocationContext enhanced with location labels used by OPENRESEARCH
        '''
        locationContext = LocationContext.fromCache()
        if locationContext is None:
            return
        # for locations in locationContext.countries, locationContext.regions, locationContext.cities:
        #     for location in locations:
        #         LocationFixer._addPageTitleToLabels((location))
        #         LocationFixer._addCommonNamesToLabels((location))
        return locationContext

    @staticmethod
    def _addPageTitleToLabels(location: Location):
        '''
        Adds the pageTitle of the given location to the labels of the given location
        '''
        pageTitle = LocationFixer.getPageTitle(location)
        LocationFixer._addLabelToLocation(location, pageTitle)

    @staticmethod
    def _addCommonNamesToLabels(location: Location):
        '''
        Add commonly used names to the labels
        '''
        if isinstance(location, Country):
            label = f"Category:{location.name}"
            LocationFixer._addLabelToLocation(location, label)

    @staticmethod
    def _addLabelToLocation(location: Location, *label: str):
        '''
        Adds the given labels to the given location
        '''
        for l in label:
            if 'labels' in location.__dict__:
                labels = location.__dict__['labels']
                if isinstance(labels, list):
                    labels.append(l)
                else:
                    labels = [l, labels]
                location.__dict__['labels'] = labels
            else:
                location.__dict__['labels'] = [l]

    
if __name__ == '__main__':
    PageFixerManager.runCmdLine([LocationFixer])